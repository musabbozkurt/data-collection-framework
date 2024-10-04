### Prerequisites

- `Python3` or higher version
- `Pycharm IDE/IntelliJ IDEA` (Recommended)
- `Docker` should be installed
    - Run `docker-compose up --build` instead of `XAMPP`
- MongoDB
    - `Url`: http://localhost:8081 or http://0.0.0.0:8081/
    - `username`: `mexpress`
    - `password`: `mexpress`
- MariaDB
    - `MARIADB_DATABASE`: `root_db`
    - `MARIADB_USER`: `user`
    - `MARIADB_PASSWORD`: `user`
- phpMyAdmin
    - http://localhost:8080/
    - Run [testdb.sql](db_scripts/testdb.sql)
- php-app
    - http://localhost:3000/
    - Sign up
    - Sign in

---

### Update [ConfigFile.config](data_collection_framework/config/ConfigFile.config) with your configs

- `filePathForTimelineOutputs` = Enter folder path for timeline i.e. user path/timeline/
- `filePathForFollowersOutputs` = Enter folder path for followers i.e user path/followers/
- `filePathForListOfUsername` = Enter filepath for userList file. userList file can be text file contains Twitter
  usernames
- `filePathForMongo` = filepath/of/text/files/to/store/mongodb/*.txt
- `filePathForTokenization` = enter file path which contains text files
- `filePathForCrossVal` = filepath must contains at least 2 folder which are containing text files
- `wordListForStreaming` = ['python', 'java', '#java', 'javascript'] you can add whatever term do you want inside that
  list

- Twitter API credentials (`Please enter your keys and DON'T SHARE THEM`)
    * `consumer_key` =
    * `consumer_secret` =
    * `access_key` =
    * `access_secret` =

---
