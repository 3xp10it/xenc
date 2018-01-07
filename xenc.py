import re
import sys
from flask import Flask
from flask import request
import frida
from urllib.parse import quote
from exp10it import send_http_package
from exp10it import get_param_list_from_param_part
from exp10it import CLIOutput

output = CLIOutput()
app = Flask(__name__)


example_script_string = """'use strict';

rpc.exports = {
    encrypt: function (plain) {
        var result=ObjC.classes.PARSCryptDataUtils.encryptWithServerTimestamp_(plain)
        return result.toString()
    },
    add: function (a, b) {
            return a + b;
        }
};
"""

pid = input("Please input your target process pid in your usb device(ps aux | egrep '^mobile.*ProcessNameHere.*'):\n > ")
try:
    session = frida.get_usb_device().attach(int(pid))
except Exception as e:
    print(e)
    sys.exit(0)
print(example_script_string)
js_file = input(
    "Upon is a js example file,please input your frida js file containing the rpc function:\n > ")
with open(js_file, "r+") as f:
    script_string = f.read()
script = session.create_script(script_string)
function_list = re.findall(r"([^\s:]+):\s*function", script_string, re.I)
script.load()
http_or_https = input(
    "Please input your request is 'http' or 'https':\ndefault['https'] > ") or "https"
encrypt_type = input(
    "Please input encrypt type:\n1.Only part of get|post parameter value should be encrypted\n2.All post content should be encrypted\ndefault[1] > ") or "1"
if encrypt_type == "1":
    origin_request_file = input(
        "Please input a request package file :\ndefault[request.txt] > ") or "request.txt"
    with open(origin_request_file, "r+") as f:
        origin_request = f.read()
    origin_string = input(
        "Please input the query string to be encrypted(eg.a=1&b=&c=2):\n > ")

    param_list = get_param_list_from_param_part(origin_string)
    new_request_to_check = origin_request
    for param in param_list:
        new_request_to_check = re.sub(
            r"%s=[^&]+" % param, re.search(r"(%s=[^&]*)" % param, origin_string).group(1), new_request_to_check)
    new_request_to_check = re.sub(
        r"Host: \S+", "Host: 127.0.0.1:5000", new_request_to_check)
    param_and_encrypt_function_list = []
    for param in param_list:
        sys.stdout.write(
            "Please input encrypt function for parameter '%s',the function list in js is " % param)
        output.good_print(str(function_list) + ":")
        param_encrypt_function = input(" > ")
        param_and_encrypt_function_list.append((param, param_encrypt_function))
    output.good_print(
        "\nThe content of the request packet you need to exploit is:\n")
    output.good_print(new_request_to_check, "red")
elif encrypt_type == '2':
    origin_request_file = input(
        "Please input the request package file before encryption :\n > ")
    with open(origin_request_file, "r+") as f:
        origin_request = f.read()
    sys.stdout.write(
        "Please input the encryption function for the entire 'data' in the 'post' request packet,the function list in js is ")
    output.good_print(str(function_list) + ":")
    post_data_encrypt_function = input(" > ")
    output.good_print(
        "\nThe content of the request packet you need to exploit is:\n")
    output.good_print(origin_request, "red")


@app.route('/')
def tansfer():
    headers = str(request.headers)
    data = str(request.data.decode("utf-8"))
    if encrypt_type == "1":
        new_request_to_send = origin_request
        for param_and_encrypt_function in param_and_encrypt_function_list:
            param = param_and_encrypt_function[0]
            encrypt_function = param_and_encrypt_function[1]
            orignal_param_value = request.args[param]
            encrypt_function = getattr(script.exports, encrypt_function)
            encrypt_param_value = encrypt_function(orignal_param_value)
            encrypt_param_value = quote(encrypt_param_value)
            encrypt_string = param + "=" + encrypt_param_value
            new_request_to_send = re.sub(
                r"%s=[^&]+" % param, encrypt_string, new_request_to_send)
        output.good_print("\nNew request send by python:\n", "blue")
        output.good_print(new_request_to_send + "\n")
        return_value = send_http_package(new_request_to_send, http_or_https)
        return return_value
    elif encrypt_type == "2":
        global post_data_encrypt_function
        post_data_encrypt_function = getattr(
            script.exports, post_data_encrypt_function)
        headers = re.search(r"([\s\S]+\n\n)\S+", origin_request).group(1)
        data = post_data_encrypt_function(data)
        new_request_to_send = headers + data
        output.good_print("\nNew request send by python:\n", "blue")
        output.good_print(new_request_to_send + "\n")
        return_value = send_http_package(new_request_to_send, http_or_https)
        return return_value


if __name__ == '__main__':
    app.run()
