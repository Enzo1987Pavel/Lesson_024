import os
import re

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def set_command(cmd: str, value: str, query: list[str]) -> list:
    if cmd == "filter":
        result = list(filter(lambda str_data: value in str_data, query))
    elif cmd == "map":
        col_number = int(value)
        result = list(map(lambda str_data: str_data.split()[col_number], query))
    elif cmd == "unique":
        result = list(set(query))
    elif cmd == "sort":
        reverse = (value == "asc")  # asc - прямой порядок, desc - обратный порядок
        result = list(sorted(query, reverse=reverse))
    elif cmd == "limit":
        result = query[:(int(value))]
    elif cmd == "regex":
        result = list(filter(lambda str_value: re.search(value, str_value), query))
    else:
        BadRequest("Введен неверный запрос!")

    return result


def set_query(params):
    with open(os.path.join(DATA_DIR, params["file_name"])) as file:
        file_data = file.readlines()

    res = file_data

    if "cmd1" in params.keys():
        res = set_command(params["cmd1"], params["value1"], res)

    if "cmd2" in params.keys():
        res = set_command(params["cmd2"], params["value2"], res)

    if "cmd3" in params.keys():
        res = set_command(params["cmd3"], params["value3"], res)

    return list(res)


@app.route("/perform_query/", methods=["POST"])
def perform_query():
    # получить параметры query и file_name из request.args, при ошибке вернуть ошибку 400
    # проверить, что файла file_name существует в папке DATA_DIR, при ошибке вернуть ошибку 400

    query: dict = request.json
    file_name: str = query["file_name"]

    if query is None:
        raise BadRequest("Не задан запрос!")

    if not os.path.exists(os.path.join(DATA_DIR, file_name)):
        raise BadRequest("Не найден файл с данными по указанному пути!")

    return jsonify(set_query(query))


if __name__ == "__main__":
    app.run()
