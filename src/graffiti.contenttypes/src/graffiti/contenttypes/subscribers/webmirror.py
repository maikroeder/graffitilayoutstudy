def webmirror_added_handler(obj, _):
    try:
        obj.extract_webmirror(force=True)
    except Exception as e:
        print(e)


def webmirror_modified_handler(obj, _):
    try:
        obj.extract_webmirror(force=True)
    except Exception as e:
        print(e)
