import requests
import sys
import json
import getopt


def dump_swagger_from_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        print("Bad Request", r.status_code, r.reason, r.text)
        raise Exception("Bad Request, please check your url: " + url)
    try:
        content = r.content
        if isinstance(content, bytes):
            content = content.decode()
        json_dict = json.loads(content)
    except Exception as e:
        print("Bad Swagger Json Content")
        print(e)
        raise Exception("Bad Json Format, please check your web content")
    return json_dict


def save_swagger_json_to_file(json_dict, target_file="swagger2.json"):
    with open(target_file, "w") as fd:
        fd.write(json.dumps(json_dict, indent=4))


def main():
    default_dst_file = "swagger2.json"
    Usage = """
    swagger-dump -u <source_url> -d <dst_file>
    """

    opts, args = getopt.getopt(sys.argv[1:], 'hu:d:',
          [
            'src-url=',
            'dst-file=',
            'help'
            ]
          )
    src_url = None
    dst_file =default_dst_file

    for option, value in opts:
        if  option in ["-h", "--help"]:
            print(Usage)
            sys.exit(1)
        elif option in ['--src-url', '-u']:
            src_url = value
        elif option in ['--dst-file', '-d']:
            dst_file = value
        else:
            print(Usage)
            print("Unknown option {}".format(option))
            sys.exit(1)
    if not src_url:
        print(Usage)
        print("Error: -u source url is required")
        sys.exit(1)

    json_dict = dump_swagger_from_url(src_url)
    save_swagger_json_to_file(json_dict, dst_file)
    print("Swagger api doc has been saved to {}\n".format(dst_file))


if __name__ == "__main__":
    main()