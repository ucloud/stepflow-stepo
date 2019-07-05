import subprocess
import time
import json

processes = dict()
result = dict()

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    req_object = json.loads(str(req, encoding = "utf-8"))
    if req_object.get("action") is None:
        res = json.dumps({
            "retCode": -1,
            "message": "Invalid action."
        })
    action = req_object["action"]

    if action == "RunCommand":
        if req_object.get("command") is None or req_object.get("path") is None:
            res = json.dumps({
                "retCode": -1,
                "message": "Command or path is missing."
            })
            return res
        command = req_object["command"]
        path = req_object["path"]
        args = ""
        if req_object.get("args") is not None:
            args = req_object["args"]
        args_array = args.split(" ")
        id = run_command(command, path, args_array)
        if id is None:
            res = json.dumps({
                "retCode": -1,
                "message": "Action failed." 
            })
            return res
        else:
            res = json.dumps({
                "retcode": 0,
                "id": id,
            })
            return res

    if action == "GetStatus":
        if req_object.get("id") is None:
            res = json.dumps({
                "retcode": -1,
            })
            return res
        code, out, err = check(req_object["id"])
        if code is None:
            if err is not None:
                res = json.dumps({
                    "retcode": -1,
                    "code": code,
                    "stdout": out,
                    "stderr": err,
                })
                return res
            res = json.dumps({
                "retcode": 1,
                "code": code,
                "stdout": out,
                "stderr": err,
            })
            return res
        else:
            res = json.dumps({
                "retcode": 0,
                "code": code,
                "stdout": out,
                "stderr": err,
            })
            return res
    
    return json.dumps({
        "retcode": -1,
        "message": "Invalid action."
    })

def run_command(command, path, args):
    proc = subprocess.Popen([command, path] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processes[proc.pid] = proc
    return proc.pid

def check(id):
    if processes.get(id) is None:
        return None, None, "Invalid ID."
    else:
        proc = processes[id]
        return_code = proc.poll()
        if return_code is None:
            return None, None, None
        else:
            out, err = proc.communicate()
            processes.pop(id, None)
            return return_code, str(out, encoding = "utf-8"), str(err, encoding = "utf-8")
        






