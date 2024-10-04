### Prerequisites

- `Python 3+` should be installed
- `Pycharm IDE, IntelliJ IDEA, etc.` can be installed to open the project (Recommended)
- Update the following `Twitter API` credentials with your configs (`DON'T SHARE THEM`)
  in [ConfigFile.config](data_collection_framework/config/ConfigFile.config) file
    * `consumer_key` =
    * `consumer_secret` =
    * `access_key` =
    * `access_secret` =
- `Docker` should be installed
    - Run `docker-compose up --build` command

---

- [docker-compose.yml](docker-compose.yml) contains the followings
    - MongoDB
        - `url`: http://localhost:8081/ or http://0.0.0.0:8081/
        - `username`: `mexpress`
        - `password`: `mexpress`
    - MariaDB
        - `MARIADB_DATABASE`: `root_db`
        - `MARIADB_USER`: `user`
        - `MARIADB_PASSWORD`: `user`
    - phpMyAdmin
        - http://localhost:8080/
    - php-app
        - http://localhost:3000/
        - Sign up
        - Sign in

---

### Other variables in [ConfigFile.config](data_collection_framework/config/ConfigFile.config) file can be reviewed

- `word_list_for_streaming` = `['python', 'java', '#java', 'javascript']` modify the list according to the needs
- `file_path_for_timeline_outputs` = Path for timeline i.e. user path/timeline/
- `file_path_for_followers_outputs` = Path for followers i.e user path/followers/
- `file_path_for_list_of_username` = Path for userList file can be text file contains Twitter usernames
- `file_path_for_mongo` = filepath/of/text/files/to/store/mongodb/*.txt
- `file_path_for_tokenization` = File path contains text files
- `file_path_for_cross_val` = File path must have at least 2 folders contains text files

---
