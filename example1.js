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

