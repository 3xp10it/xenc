import re
import sys
import frida
from urllib.parse import quote
from exp10it import send_http_package
from exp10it import CLIOutput


output = CLIOutput()
pid = input("Please input your target process pid in your usb device(ps aux | egrep '^mobile.*ProcessNameHere.*'):\n > ")
try:
    session = frida.get_usb_device().attach(int(pid))
except Exception as e:
    print(e)
    sys.exit(0)
http_or_https = input(
    "Please input your request is 'http' or 'https':\ndefault['https'] > ") or "https"
encrypt_type = input(
    "Please input encrypt type:\n1.Only part of get|post parameter value should be encrypted\n2.All post content should be encrypted\ndefault[1] > ") or "1"

with open("example1.js", "r+") as f:
    example_script_string = f.read()
print(example_script_string)
js_file = input(
    "Upon is a js example file,please input your frida js file containing the rpc function:\n > ")
with open(js_file, "r+") as f:
    script_string = f.read()

if encrypt_type == "1":
    param_string = input(
        "Please input the parameter you want to encrypt,split with 'Space',eg.->id name<-:\n > ")
    script = session.create_script(script_string)
    rpc_string = re.search(
        r"(rpc\.exports[\S\s]+)", script_string, re.I).group(1)
    function_list = re.findall(r"([^\s:]+):\s*function", rpc_string, re.I)
    function_list = [function for function in function_list if function not in [
        'onEnter', 'onLeave']]
    script.load()
    param_list = re.split(r"\s", param_string)
    param_and_encrypt_function_list = []
    for param in param_list:
        sys.stdout.write(
            "Please input encrypt function for parameter '%s',the function list in js is " % param)
        output.good_print(str(function_list) + ":")
        param_encrypt_function = input(" > ")
        param_and_encrypt_function_list.append((param, param_encrypt_function))

elif encrypt_type == '2':
    script = session.create_script(script_string)
    script.load()
    rpc_string = re.search(
        r"(rpc\.exports[\S\s]+)", script_string, re.I).group(1)
    function_list = re.findall(r"([^\s:]+):\s*function", rpc_string, re.I)
    function_list = [function for function in function_list if function not in [
        'onEnter', 'onLeave']]
    sys.stdout.write(
        "Please input the encryption function for the entire 'data' in the 'post' request packet,the function list in js is ")
    output.good_print(str(function_list) + ":")
    post_data_encrypt_function = input(" > ")


def start_transfer_server():
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class S(BaseHTTPRequestHandler):
        def _set_headers(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_POST(self):
            headers = str(self.headers)
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            request_before_encrypt = self.requestline + "\n" + headers + data.decode()

            if encrypt_type == "1":
                # 未加密的request需要安全人员提供,eg.直接在burpsuite的repeater中发包,Host为127.0.0.1:8888,Real-Host为真正的服务器
                request_after_encrypt = request_before_encrypt
                for param_and_encrypt_function in param_and_encrypt_function_list:
                    param = param_and_encrypt_function[0]
                    encrypt_function = param_and_encrypt_function[1]
                    orignal_param_value = re.search(
                        r"%s=([^&]*)" % param, request_before_encrypt).group(1)
                    # 注意,js代码中的rpc函数名不能有大写字母和下划线,最好由小写字母和数字组成
                    encrypt_function = getattr(
                        script.exports, encrypt_function)
                    encrypt_param_value = encrypt_function(orignal_param_value)
                    encrypt_param_value = quote(encrypt_param_value)
                    encrypt_string = param + "=" + encrypt_param_value
                    request_after_encrypt = re.sub(
                        r"%s=[^&]+" % param, encrypt_string, request_after_encrypt)
                real_server_host = re.search(
                    r"Real-Host: (\S+)", request_after_encrypt).group(1)
                request_after_encrypt = re.sub(r"Host: \S+((\n)|(\r\n))Real-Host: \S+",
                                               "Host: %s" % real_server_host, request_after_encrypt)
                output.good_print("\nNew request send by python:\n", "blue")
                output.good_print(request_after_encrypt + "\n")
                return_value = send_http_package(
                    request_after_encrypt, http_or_https)
                print(return_value)
                self._set_headers()
                self.wfile.write(bytes(return_value, "utf-8"))

            elif encrypt_type == "2":
                # 未加密的request需要安全人员提供,eg.直接在burpsuite的repeater中发包,Host为127.0.0.1:8888,Real-Host为真正的服务器
                _ = re.search(r"([\S\s]+)((\r\n\r\n)|(\n\n))(.+)",
                              request_before_encrypt)
                headers = _.group(1) + _.group(2)
                data = _.group(5)
                real_server_host = re.search(
                    r"Real-Host: (\S+)", request_before_encrypt).group(1)
                headers = re.sub(r"Host: \S+((\n)|(\r\n))Real-Host: \S+",
                                 "Host: %s" % real_server_host, headers)
                global post_data_encrypt_function
                encrypt_post_data = getattr(
                    script.exports, post_data_encrypt_function)
                data = encrypt_post_data(data)
                request_after_encrypt = headers + data
                output.good_print("\nNew request send by python:\n", "blue")
                output.good_print(request_after_encrypt + "\n")
                return_value = send_http_package(
                    request_after_encrypt, http_or_https)
                print(return_value)
                self._set_headers()
                self.wfile.write(bytes(return_value, "utf-8"))

    def run(server_class=HTTPServer, handler_class=S, port=8888):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print('Starting httpd...')
        httpd.serve_forever()

    run()


start_transfer_server()
