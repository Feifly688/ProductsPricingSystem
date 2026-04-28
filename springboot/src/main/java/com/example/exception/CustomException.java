/**
 * CustomException
 *
 * @author Feiqi
 * @date 2024/10/07  下午 9:43
 */
package com.example.exception;

public class CustomException extends RuntimeException {
    private String msg;

    public CustomException(String msg) {
        this.msg = msg;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }
}
