/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('otp_auth.wk_otp_login', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var session = require('web.session');
    $(document).ready(function () {
        // $(".field-login>label").text('Mobile Number');
        // $(".field-login>input").attr('placeholder','Mobile Number');

        if ($('#otplogincounter').get(0)) {
            // get number form URL
            if (new URL(window.location.href).searchParams.get("number")) {
                console.log("we get the number!");
                $(".field-login>input").val(new URL(window.location.href).searchParams.get("number"));
                $(".field-login").before("<p id='mk_exit_alert' class='alert alert-success'>Already find a account, please login</p>");
                setTimeout(function () {
                    $('#mk_exit_alert').slideUp('slow');
                }, 3000);
            }
            $(":submit").hide();
            // $(".field-login>label").text('Mobile or Email');
            // $(".field-login>input").attr('placeholder','mobile or email');
            // $(".field-password").hide();
            $(".oe_login_form").wrapInner("<div class='container' id='wk_container'></div>");
            $(".field-login").before("<i class='fa fa-arrow-left text-primary wk_back_btn' aria-hidden='true'></i>");
            $(".wk_back_btn").hide();
            $("#password").addClass('wkpassword');
        }
        $('.wk_next_btn').on('click', function (e) {
            console.log("Next Button Clicked")
            if ($(".field-otp-option").css("display") == 'none') {
                $(".field-login").hide();
                $(".wk_back_btn").show();
                $(".field-otp-option").css("display", "");
                // revoke email
                var email = $('#login').val();
                if (email.includes("@") === false) {
                    ajax.jsonRpc("/get/login", 'call', { 'email': email })
                        .then(function (data) {
                            if (data) {
                                email = data.email.login
                                $('#login').val(data.email.login)
                            }
                        })
                }
            } else {
                var radioVal = $('input[name=radio-otp]:checked').val();
                if (radioVal == 'radiotp') {
                    generateLoginOtp();
                } else if (radioVal == 'radiopwd') {
                    $(".field-password").show();
                    $("#password").attr('placeholder', 'Enter Password');
                    $(":submit").show();
                    $(".wk_next_btn").hide();
//                    $(".field-otp-option").css("display", "none");
                }
            }
        });


        $('.wk_back_btn').on('click', function (e) {
            $('#wk_error').remove();
            $('.wk_login_resend').remove();
            if ($(".field-otp-option").css("display") != 'none') {
                $(".field-login").show();
                $(".wk_back_btn").hide();
                $(".field-otp-option").css("display", "none");
            } else if ($(".field-otp-option").css("display") == 'none') {
                $(".field-otp-option").css("display", "");
                $(".field-password").hide();
                $(":submit").hide();
                $(".wk_next_btn").show();
            }
        });
        // if (!$('.oe_signup_form').length) {
        //     $('label[for=password], input#password').text("OTP");
        // }
        $('input:radio[name="radio-otp"]').change(function () {
            if ($(this).val() == 'radiotp') {
                console.log("OTP Selected......")
                $('label[for=password], input#password').text("OTP");
            } else if ($(this).val() == 'radiopwd') {
                $('label[for=password], input#password').text("Password");
            }
        });

        $(this).on('click', '.wk_login_resend', function (e) {
            generateLoginOtp();
        });
        $('label[for="password"]').show();

    });

    function generateLoginOtp() {
        var mobile = $('#mobile').val();
        var email = $('#login').val();
        var otp_type = $('.otp_type').val();

        // Get Actual Login and Mobile
        if (email.includes("@") === false) {
            ajax.jsonRpc("/get/login", 'call', { 'email': email })
                .then(function (data) {
                    if (data) {
                        mobile = email;
                        email = data.email.login
                        $('#login').val(data.email.login)
                    }
                })
        }

        $("div#wk_loader").addClass('show');
        ajax.jsonRpc("/send/otp", 'call', { 'email': email, "loginOTP": 'loginOTP', 'mobile': mobile })
            .then(function (data) {
                if (data) {
                    if (data.email) {
                        if (data.email.status == 1) {
                            $("div#wk_loader").removeClass('show');
                            $('#wk_error').remove();
                            getLoginInterval(data.email.otp_time);
                            $(".field-password").show();
                            $(".field-password>label").text('Enter Otp');
                            $("#password").attr('placeholder', 'Enter OTP');
                            if (otp_type == '4') {
                                $("#password").attr("type", "text");
                            }
                            $(".field-password").after("<p id='wk_error' class='alert alert-success'>" + data.email.message + "</p>");
                            $(":submit").show();
                            $(":submit").removeAttr("disabled")
                            $(".wk_next_btn").hide();
                            $(".field-otp-option").css("display", "none");
                        } else {
                            $("div#wk_loader").removeClass('show');
                            $('#wk_error').remove();
                            $(".field-otp-option").after("<p id='wk_error' class='alert alert-danger'>" + data.email.message + "</p>");
                        }
                    }
                    if (data.mobile) {
                        if (data.mobile.status == 1) {
                            // if (data.mobile.status) {
                            //     $('label[for=login], input#login').val(data[3]);
                            // }

                            if (data.email) {
                                if (data.email.status != 1) {
                                    $("div#wk_loader").removeClass('show');
                                    $('#wk_error').remove();
                                    getLoginInterval(data.email.otp_time);
                                    $(".field-password").show();
                                    $("#passwogenerateSMSSignUpOtprd").attr('placeholder', 'Enter OTP');
                                    if (otp_type == '4') {
                                        $("#password").attr("type", "text");
                                    }
                                    $(":submit").show();
                                    $(".wk_next_btn").hide();
                                    $(".field-otp-option").css("display", "none");
                                }
                            }
                            $(".field-password").after("<p id='wk_error' class='alert alert-success'>" + data.mobile.message + "</p>");
                        }
                        else {
                            if (data.email) {
                                if (data.email.status != 1) {
                                    $("div#wk_loader").removeClass('show');
                                    $('#wk_error').remove();
                                }
                            }
                            $(".field-otp-option").after("<p id='wk_error' class='alert alert-danger'>" + data.mobile.message + "</p>");
                        }
                    }
                }
            });


        // }
    }

    function getLoginInterval(otpTimeLimit) {
        var countDown = otpTimeLimit;
        var x = setInterval(function () {
            countDown = countDown - 1;
            $("#otplogincounter").html("OTP will expire in " + countDown + " seconds.");
            if (countDown < 0) {
                clearInterval(x);
                $('#wk_error').remove();
                $("#otplogincounter").html("<a class='btn btn-link pull-right wk_login_resend' href='#'>Resend OTP</a>");
                $(":submit").attr("disabled", true);
            }
        }, 1000);
    }

})
