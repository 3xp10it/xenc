
## xenc

### Disclaimer

[!] legal disclaimer: Usage of xenc.py for attacking targets without prior mutual consent is illegal.It is the end user's responsibility to obey all applicable local, state and federal laws.Developers assume no liability and are not responsible for any misuse or damage caused by this program.

### About

xenc可用于在移动端app有加密数据情况下的安全测试,支持非对称加密,支持以下2种情况的加密情况:

**1.get或post请求中的部分参数值被加密**

``` 
example:

POST /index.php HTTP/1.1 
Host: 192.168.1.1 
Connection: close 
Accept: */* 
User-Agent: PALifeApp/4.11.0 (iPhone; iOS9.0; Scale/2.00) 
Accept-Language: zh-Hans-CN;q=1 X-Tingyun-Id: s8-utloiNb8;c=2;r=736688779 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 993

mobilePhone=Nns7415cyOT0FkzwbjiXmahxvFt6tfw1Dda8pg%2bWLBhjowZ1Y&id=1&a=2
```


**2.整个post请求的data部分被加密**

```
注意:这里认为post的整个data部分被加密前没有"部分参数值被加密"的情况
example:

POST /index.php HTTP/1.1 
Host: 192.168.1.1 
Connection: close 
Accept: */* 
User-Agent: PALifeApp/4.11.0 (iPhone; iOS9.0; Scale/2.00) 
Accept-Language: zh-Hans-CN;q=1 X-Tingyun-Id: s8-utloiNb8;c=2;r=736688779 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 993

Salted__\kÏ�D<ÜñCHÁ*'-»84}_9Óûûî#¼²åûÅ8<V«àLÎÃ¾ÐµÄ\ôÇDßç	·¨S¢À/-¢Å5¦0/B0^!{ÌÚ"³¨màK7µeª¡öê
```

### 用法

**`python3 xenc.py`**

运行后要求提供包含rpc加密函数的frida的**`js文件`**和一个**`request文件`**

#### js文件

js文件为包含frida的rpc函数的js文件,其中的rpc函数为加密函数,用来给需要加密的字符串进行加密,安全人员需要编写包含加密函数的js文件,下面是一个示例,其中包含`encrypt`和`add`两个加密函数:

```
'use strict';

rpc.exports = {
    encrypt: function (plain) {
        var result=ObjC.classes.PARSCryptDataUtils.encryptWithServerTimestamp_(plain)
        return result.toString()
    },
    add: function (a, b) {
            return a + b;
        }
};

```

#### request文件

request文件为未加密的请求包,2种不同加密情况下的请求包略有区别,具体如下:

`get或post请求中的部分参数值被加密`情况下的request示例文件

```
POST /index.php HTTP/1.1 
Host: 192.168.1.1 
Connection: close 
Accept: */* 
User-Agent: PALifeApp/4.11.0 (iPhone; iOS9.0; Scale/2.00) 
Accept-Language: zh-Hans-CN;q=1 X-Tingyun-Id: s8-utloiNb8;c=2;r=736688779 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 993

mobilePhone=Nns7415cyOT0FkzwbjiXmahxvFt6tfw1Dda8pg%2bWLBhjowZ1Y&id=1&a=2

或者其中的被加密的参数mobilePhone的值使用加密前的值也可

POST /index.php HTTP/1.1 
Host: 192.168.1.1 
Connection: close 
Accept: */* 
User-Agent: PALifeApp/4.11.0 (iPhone; iOS9.0; Scale/2.00) 
Accept-Language: zh-Hans-CN;q=1 X-Tingyun-Id: s8-utloiNb8;c=2;r=736688779 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 993

mobilePhone=17723458764&id=1&a=2
```

`整个post请求的data部分被加密`情况下的request示例文件

```
其中整个post请求中的data部分要是未加密的数据

POST /index.php HTTP/1.1 
Host: 192.168.1.1 
Connection: close 
Accept: */* 
User-Agent: PALifeApp/4.11.0 (iPhone; iOS9.0; Scale/2.00) 
Accept-Language: zh-Hans-CN;q=1 X-Tingyun-Id: s8-utloiNb8;c=2;r=736688779 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 993

page=1&name=Bob
```

### 原理

xenc.py将在`5000`端口(flask默认web端口)进行监听,xenc.py相当于一个转发器,用于将安全测试人员发送到xenc.py的request包进行适当的加密后再转发到真正的服务器,安全人员只需要对未加密前的数据进行测试,测试的host是127.0.0.1,运行`python3 xenc.py`后将以红色字体打印出需要测试的新的request包,可将这个红色的request包用于sqlmap或burpsuite等工具进行测试.
