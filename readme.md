# xenc

### Disclaimer

[!] legal disclaimer: Usage of xenc.py for attacking targets without prior mutual consent is illegal.It is the end user's responsibility to obey all applicable local, state and federal laws.Developers assume no liability and are not responsible for any misuse or damage caused by this program.

### Usage

**`python3 xenc.py`**

运行`python3 xenc.py`后要求安全人员提供一个包含rpc加密函数的frida的**js文件**和一个**request请求**

### About

xenc可用于在移动端app有加密数据情况下的安全测试,支持非对称加密,支持以下2种情况的加密情况:

#### 0x1 get或post请求中的部分参数值被加密

如下示例,其中mobilePhone和b两个参数被加密

``` 
example:

POST /index.php HTTP/1.1 
Host: www.baidu.com:443
Connection: close 
Accept: */* 
User-Agent: PALxxx/4.11.0 (iPhone; iOS9.0; Scale/2.00) 
Accept-Language: zh-Hans-CN;q=1 X-Tingyun-Id: s8-utloiNb8;c=2;r=736688779 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 993

mobilePhone=Nns7415cyOT0FkzwbjiXmahxvFt6tfw1Dda8pg%2bWLBhjowZ1Y&id=1&a=2&b=tfw1Dda8pg%2bWLBhj
```

**js文件**

需要安全人员找到需要加密的参数在app中对应的加密函数(如上面example包中需要找到mobilePhone和b这两个参数的加密函数),然后安全人员需要编写包含加密函数的js文件,下面是一个示例,其中包含`encrypt1`和`add`两个加密函数(**注意,rpc的参数名不能有大写字母和下划线**):

```
'use strict';

rpc.exports = {
    encrypt1: function (plain) {
        var result=ObjC.classes.PARSCryptDataUtils.encryptWithServerTimestamp_(plain)
        return result.toString()
    },
    add: function (a, b) {
            return a + b;
        }
};

```

**request请求**

request请求要求是一个加密参数的值为未加密值的请求,可设置加密参数的值为空或一个初始值(更好),要求对request包中的Host字段修改为`127.0.0.1:8888`,并在Host字段的下一行加一个字段`Real-Host`,并将它的内容设置为真正的服务器地址(domain/ip+port格式),然后可通过burpsuite的repeater来发包,并右键通过burpsuite来测试有无漏洞.例如上面的example包对应的需要在burpsuite中发的包的内容如下:

```
POST /index.php HTTP/1.1 
Host: 127.0.0.1:8888
Real-Host: www.baidu.com:443
Connection: close 
Accept: */* 
User-Agent: PALxxx/4.11.0 (iPhone; iOS9.0; Scale/2.00) 
Accept-Language: zh-Hans-CN;q=1 X-Tingyun-Id: s8-utloiNb8;c=2;r=736688779 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 993

mobilePhone=18765452345&id=1&a=2&b=1

```

#### 0x2 整个post请求的data部分被加密

如下示例,其中整个data内容被加密,这里认为post的整个data部分被加密前没有"部分参数值被加密"的情况

```
example:

POST /index.php HTTP/1.1 
Host: www.baidu.com:443
Connection: close 
Accept: */* 
User-Agent: PALxxx/4.11.0 (iPhone; iOS9.0; Scale/2.00) 
Accept-Language: zh-Hans-CN;q=1 X-Tingyun-Id: s8-utloiNb8;c=2;r=736688779 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 993

Salted__\kÏ�D<ÜñCHÁ*'-»84}_9Óûûî#¼²åûÅ
```


**js文件**

这里假设加密函数的参数是整个request内容(包含header和data的post请求的明文内容),且加密函数只对data部分进行加密,header部分不加密.下面是一个示例,其中包含`encrypt2`和`sub`两个加密函数(**注意,rpc的参数名不能有大写字母和下划线**):

```
'use strict';

rpc.exports = {
    encrypt2: function (plain) {
        var result=ObjC.classes.PAREncryptor.encryptHttpRequest_(plain)
        return result.toString()
    },
    sub: function (a, b) {
            return a - b;
        }
};

```

**request请求**

request请求要求是一个data部分未加密的请求,需人工通过hook找出加密前的整个data的内容,要求将request包中的Host字段修改为`127.0.0.1:8888`,并在Host字段的下一行加一个字段`Real-Host`,并将它的内容设置为真正的服务器地址(domain/ip+port格式),然后可通过burpsuite的repeater来发包,并右键通过burpsuite来测试有无漏洞.例如上面的example包对应的需要在burpsuite中发的包的内容如下:

```
POST /index.php HTTP/1.1 
Host: 127.0.0.1:8888
Real-Host: www.baidu.com:443
Connection: close 
Accept: */* 
User-Agent: PALxxx/4.11.0 (iPhone; iOS9.0; Scale/2.00) 
Accept-Language: zh-Hans-CN;q=1 X-Tingyun-Id: s8-utloiNb8;c=2;r=736688779 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 993

page=1&no=2&year=3
```
