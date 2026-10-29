"""HTTP front ends over the same command registry: REST (/api/...) and GraphQL (/graphql)."""
from typing import Annotated, Any, Dict, List, Optional

import strawberry
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON

from data_collection_framework.commands.base import CommandRegistry
from data_collection_framework.commands.definitions import build_registry
from data_collection_framework.commands.dispatch import authorized, run_command
from data_collection_framework.config.settings import Settings, get_settings

MAX_REQUEST_BYTES = 64 * 1024
BEARER = "Bearer "
AuthHeader = Annotated[Optional[str], Header()]


def bearer_token(authorization: Optional[str]) -> str:
    value = authorization or ""
    return value[len(BEARER):] if value.startswith(BEARER) else ""


API_DESCRIPTION = """
Run the framework's commands over HTTP. REST and GraphQL use the same commands and return `{ok, message}`.

* **Auth:** if `PY_SERVER_TOKEN` is set, send `Authorization: Bearer <token>` (add it as a header).
* **Request:** `POST /api/commands/<kebab-case-name>` with JSON `{"args": {"param": "value"}}`; values are sent as text/numbers.
* **Result:** HTTP 200 with `ok: true|false`; `message` is the output or the reason for failure.
* **GraphQL:** `POST /graphql`, query `commands`, mutation `run(name, args)`.
"""
TAGS = [{"name": "System", "description": "Health and discovery"},
        {"name": "Commands", "description": "One endpoint per command; the body lists its parameters"},
        {"name": "GraphQL", "description": "Same commands through one GraphQL endpoint"}]
ERRORS = {401: {"description": "Missing or wrong bearer token"},
          400: {"description": "Body is not a JSON object"},
          413: {"description": "Body larger than 64 KB"}}


class CommandReply(BaseModel):
    ok: bool = Field(description="False when the command failed or arguments were invalid")
    message: str = Field(description="Command output or the error message")


SLUGS = {
    "collecttweetfromuserlist": "collect-tweets-from-user-list",
    "collecttweetfromusername": "collect-tweets-from-username",
    "collectfollowerfromuserlist": "collect-followers-from-user-list",
    "collectfollowerfromusername": "collect-followers-from-username",
    "scrapexbatch": "scrape-x-batch",
    "scrapexprofile": "scrape-x-profile",
    "discoverprofiles": "discover-profiles",
    "addprofiles": "add-profiles",
    "listprofiles": "list-profiles",
    "scrapeselected": "scrape-selected",
    "connectx": "connect-x",
    "xsession": "x-session",
    "mongodatabases": "mongo-databases",
    "mongodocuments": "mongo-documents",
    "mongogroups": "mongo-groups",
    "mongoprofiledocuments": "mongo-profile-documents",
    "storedata": "store-data",
    "plotlanguage": "plot-language",
    "plotcountry": "plot-country",
    "plotlocation": "plot-location",
    "plottimezone": "plot-timezone",
    "plottweet": "plot-tweet",
    "plottweetcreatedat": "plot-tweet-created-at",
    "plotuserid": "plot-user-id",
    "plotstringofid": "plot-string-of-id",
    "plotusername": "plot-username",
    "plotscreenname": "plot-screen-name",
    "plotfollowerscount": "plot-followers-count",
    "plotfriendscount": "plot-friends-count",
    "plotuserlanguage": "plot-user-language",
    "plotretweet": "plot-retweet",
    "plotfavourite": "plot-favourite",
    "streamfromlist": "stream-from-list",
    "streamfrominput": "stream-from-input",
    "crossvalidation": "cross-validation",
    "termfrequency": "term-frequency",
    "mongoanalytics": "mongo-analytics",
    "listdatafiles": "list-data-files",
    "storefiles": "store-files",
    "storeupload": "store-upload",
    "getsettings": "get-settings",
    "savesettings": "save-settings",
    "listusernames": "list-usernames",
    "saveusernames": "save-usernames",
    "usernamestemplate": "usernames-template",
    "analysismetrics": "analysis-metrics",
    "collectionfields": "collection-fields",
    "mongoterms": "mongo-terms",
    "tweetauthors": "tweet-authors",
    "mongocrossvalidation": "mongo-cross-validation",
}
NAMES = {slug: name for name, slug in SLUGS.items()}
EXAMPLES = {
    "tweet_count": 100, "username": "NASA", "keywords": "python,docker", "limit": 50, "max_tweets": 20,
    "resume": "no", "letter": "N", "keyword": "space", "page": 1, "page_size": 20, "usernames": "NASA,SpaceX",
    "browser": "chromium", "database": "tweets_db", "collection": "tweets", "bars": 10,
    "filename": "keywords.txt", "end_time": "2030-01-01 12:00:00", "folds": 5, "splits": 10, "test_size": 0.3,
    "random_state": 1, "train_test_size": 0.2, "svm_c": 1.0, "most_common": 20, "max_pairs": 50,
    "search_word": "python", "metric": "language", "top": 10, "n": 10, "files": "tweets.json",
    "data": "{}", "text_field": "text", "label_field": "lang"}


def slug_of(name: str) -> str:
    return SLUGS.get(name, name)


def command_example(command) -> Dict[str, Any]:
    return {"args": {param.name: EXAMPLES.get(param.name, "...") for param in command.params}}


def command_description(command) -> str:
    lines = [f"Runs `{command.name}` (the old name `{command.name}` also works)."]
    if command.params:
        lines.append("\n\n**Parameters** (in `args`):\n")
        lines += [f"* `{param.name}`: {param.label}" for param in command.params]
    else:
        lines.append(" Takes no parameters; send `{}`.")
    return "\n".join(lines)


def request_body(command) -> Dict[str, Any]:
    props = {param.name: {"type": "string", "description": param.label} for param in command.params}
    schema = {"type": "object", "properties": {"args": {
        "type": "object", "properties": props, "required": list(props),
        "example": command_example(command)["args"]}}}
    return {"requestBody": {"required": bool(props), "content": {"application/json": {
        "schema": schema, "example": command_example(command)}}}}


def run_for(handler, name: str):
    async def run_named(request: Request, authorization: AuthHeader = None) -> Dict[str, Any]:
        return await handler(name, request, authorization)

    return run_named


def describe(registry: CommandRegistry) -> List[Dict[str, Any]]:
    return [{"name": command.name, "title": command.title,
             "params": [{"name": param.name, "label": param.label} for param in command.params]}
            for command in registry.all()]


@strawberry.type
class ParamInfo:
    name: str
    label: str


@strawberry.type
class CommandInfo:
    name: str
    title: str
    params: List[ParamInfo]


@strawberry.type
class CommandResult:
    ok: bool
    message: str


def build_schema(registry: CommandRegistry, settings: Settings) -> strawberry.Schema:
    def token_of(info) -> str:
        return bearer_token(info.context["request"].headers.get("authorization"))

    @strawberry.type
    class Query:
        @strawberry.field(description="Every command with its parameters")
        def commands(self, info: strawberry.Info) -> List[CommandInfo]:
            if not authorized(settings, token_of(info)):
                raise PermissionError("Unauthorized")
            return [CommandInfo(name=item["name"], title=item["title"],
                                params=[ParamInfo(**param) for param in item["params"]])
                    for item in describe(registry)]

    @strawberry.type
    class Mutation:
        @strawberry.mutation(description="Run a command; the reply has the same ok/message shape as REST and TCP")
        async def run(self, info: strawberry.Info, name: str, args: Optional[JSON] = None) -> CommandResult:
            reply = await run_in_threadpool(run_command, registry, settings, name, args, token_of(info))
            return CommandResult(**reply)

    return strawberry.Schema(query=Query, mutation=Mutation)


def create_app(settings: Optional[Settings] = None, registry: Optional[CommandRegistry] = None) -> FastAPI:
    settings = settings or get_settings()
    registry = registry or build_registry(settings)
    app = FastAPI(title="Data Collection Framework API", docs_url="/docs", redoc_url=None,
                  description=API_DESCRIPTION, openapi_tags=TAGS)

    @app.get("/health", tags=["System"], summary="Health check",
             description="No token needed. Returns `status` and how many commands are registered.")
    def health() -> Dict[str, Any]:
        return {"status": "ok", "commands": len(registry.all())}

    @app.get("/api/commands", tags=["System"], summary="List commands",
             description="Every command with its title and parameter names. Needs the bearer token if one is set.",
             responses=ERRORS)
    def commands(authorization: AuthHeader = None) -> List[Dict[str, Any]]:
        if not authorized(settings, bearer_token(authorization)):
            raise HTTPException(status_code=401, detail="Unauthorized")
        return describe(registry)

    @app.post("/api/commands/{name}", include_in_schema=False)
    async def run(name: str, request: Request, authorization: AuthHeader = None) -> Dict[str, Any]:
        if not authorized(settings, bearer_token(authorization)):
            raise HTTPException(status_code=401, detail="Unauthorized")
        body = await request.body()
        if len(body) > MAX_REQUEST_BYTES:
            raise HTTPException(status_code=413, detail="Request too large")
        try:
            payload = await request.json() if body else {}
        except ValueError:
            raise HTTPException(status_code=400, detail="Request is not valid JSON") from None
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Request must be a JSON object")
        return await run_in_threadpool(run_command, registry, settings, NAMES.get(name, name), payload.get("args"),
                                       bearer_token(authorization))

    for command in registry.all():
        app.add_api_route(
            f"/api/commands/{slug_of(command.name)}", run_for(run, command.name), methods=["POST"], tags=["Commands"],
            summary=command.title, description=command_description(command), responses=ERRORS,
            response_model=CommandReply, openapi_extra=request_body(command))

    def context(request: Request) -> Dict[str, Any]:
        return {"request": request}

    app.include_router(GraphQLRouter(build_schema(registry, settings), context_getter=context), prefix="/graphql",
                       tags=["GraphQL"])
    return app
