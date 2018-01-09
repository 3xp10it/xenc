'use strict';

rpc.exports = {
    encrypt2: function (plain) {
        var result=ObjC.classes.PARSCryptDataUtils.encryptWithServerTimestamp_(plain)
        return result.toString()
    },
    sub: function (a,b) {
        return a-b;
        }
};

