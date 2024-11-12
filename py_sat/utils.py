from typing import Any, Dict, List


def parse_json_api_response(response: dict) -> Dict[str, Any]:
    """
    Parse JSON API response to dictionary

    :param response: JSON API response
    :return: aggregate dictionary of id, type, and attributes
    """
    data = response.get("data", {})
    return __parse_json_api_dict(data)


def parse_json_api_list_response(response: dict) -> List[Dict[str, Any]]:
    """
    Parse JSON API list response to list of dictionary

    :param response: JSON API response
    :return: aggregate dictionary of id, type, and attributes
    """
    data = response.get("data", [])

    return [__parse_json_api_dict(item) for item in data]


def __parse_json_api_dict(data):
    id = data.get("id", "")
    type = data.get("type", "")
    attributes = data.get("attributes", {})
    return {"id": id, "type": type, **attributes}


def generate_json_api_request(request: dict) -> Dict[str, Any]:
    """
    Generate JSON API request from dictionary

    :param request: normal dictionary
    :return: JSON API request format
    """
    id = extract_id(request)
    type = extract_type(request)

    data = {}
    if id is not None:
        data["id"] = id
    if type is not None:
        data["type"] = type

    # Omit none values
    attribute = {k: v for k, v in request.items() if v is not None}
    data["attributes"] = attribute

    return {"data": data}


def extract_type(request):
    type = None
    if "type" in request:
        type = request.get("type", None)
        del request["type"]
    return type


def extract_id(request):
    id = None
    if "id" in request:
        id = request.get("id", None)
        del request["id"]
    if "request_id" in request:
        id = request.get("request_id", None)
        del request["request_id"]
    return id
