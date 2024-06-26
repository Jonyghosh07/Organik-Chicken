/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('otp_auth.wk_otp', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    $(document).ready(function() {
        var ValidUser = 0;
        if ($('#otpcounter').get(0)) {
            // $("#otpcounter").html("<a class='btn btn-primary btn-block wk_send' href='#'>Send OTP</a>");
            // $(":submit").attr("disabled", true).css("display","none");
            // $("#otp").css("display","none");
            $(".oe_signup_form").wrapInner("<div class='container' id='wk_container'></div>");
        }

        // $('.wk_send').on('click', function(e) {
        //     if ($(this).closest('form').hasClass('oe_reset_password_form')) {
        //         ValidUser = 1;
        //     }
        //     var email = $('#login').val();
        //     if (email) {
        //         if (validateEmail(email)) {
        //             generateOtp(ValidUser);
        //         } else {
        //             $('#wk_error').remove();
        //             $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter a valid mobile number.</p>");
        //         }
        //     } else {
        //         $('#wk_error').remove();
        //         $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter an mobile number.</p>");
        //     }
        // });

        // $('.wk_send').on('click', function(e) {
        //     if ($(this).closest('form').hasClass('oe_reset_password_form')) {
        //         ValidUser = 1;
        //     }
        //     var email = $('#login').val();
        //     if (email) {
        //         if (validateEmail(email)) {
        //             generateOtp(ValidUser);
        //         } else {
        //             $('#wk_error').remove();
        //             $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter a valid mobile number.</p>");
        //         }
        //     } else {
        //         $('#wk_error').remove();
        //         $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter an mobile number.</p>");
        //     }
        // });

        $("#submitBtn").on('click', function(e) {
            if ($(this).closest('form').hasClass('oe_reset_password_form')) {
                ValidUser = 1;
            }
            var login = $('#login').val();
            if (login) {
                if (validateEmail(login)) {
                    generateOtp(ValidUser);
                } else {
                    $('#wk_error').remove();
                    $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter a valid mobile number.</p>");
                }
            } else {
                $('#wk_error').remove();
                $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter an mobile number.</p>");
            }
        });

        $(this).on('click', '.wk_resend', function(e) {
            $(".wkcheck").remove();
            generateOtp(ValidUser);
        });
        verifyOtp();
    });

    function validateEmail(emailId) {
        var mailRegex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;


        if (emailId.toLowerCase().match(mailRegex)) {
            return true
        } else {
            return false
        }

        // return true
    };

    function validateMobile(mobileNo) {
        var mailRegex = /^\d{11}$/;

        if (mobileNo.match(mailRegex)) {
            return true
        } else {
            return false
        }
    };

    function getInterval(otpTimeLimit) {
        var countDown = otpTimeLimit;
        var x = setInterval(function() {
            countDown = countDown - 1;
            $("#otpcounter").html("OTP will expire in " + countDown + " seconds.");
            if (countDown < 0) {
                clearInterval(x);
                $("#otpcounter").html("<a class='btn btn-link pull-right wk_resend position-relative' href='#'>Resend OTP</a>");
                $("#otpcounter").append('<span>Otp is expire.Please Click on resend button</span>');
                $(":submit").attr("disabled", true);
            }
        }, 1000);
    }

    function generateOtp(ValidUser) {
        var email = $('#login').val();
        var mobile = $('#mobile').val();
        var userName = $('#name').val();
        var country_id = $('#country_id').val();
        $("div#wk_loader").addClass('show');
        $('#wk_error').remove();
        $('.alert.alert-danger').remove();

        ajax.jsonRpc("/otp_auth/generate/otp", 'call', { 'email': email, 'userName': userName, 'mobile': mobile, 'country': country_id, 'validUser': ValidUser })
            .then(function(data) {
                if (data[0] == 1) {
                    $("div#wk_loader").removeClass('show');
                    $('.wk_send').remove();
                    getInterval(data[2]);
                    $("#wkotp").after("<p id='wk_error' class='alert alert-success'>" + data[1] + "</p>");
                    $("#otp").css("display", "");
                    $('#otp').after($('#otpcounter'));
                    //Show Signup button 
                    $(":submit").attr("disabled", false).css("display", "block")
                } else {
                    if (data[1] == "Another user is already registered using this mobile number.") {
                        window.location.replace(`/web/login?number=${email}`);
                    }
                    $("div#wk_loader").removeClass('show');
                    $('#wk_error').remove();
                    $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>" + data[1] + "</p>");
                }
            });
    }

    function verifyOtp() {
        $('#otp').bind('input propertychange', function() {
            if ($(this).val().length == 6) {
                var otp = $(this).val();
                ajax.jsonRpc("/verify/otp", 'call', { 'otp': otp })
                    .then(function(data) {
                        if (data) {
                            $('#otp').after("<i class='fa fa-check-circle wkcheck' aria-hidden='true'></i>");
                            $(".wkcheck").css("color", "#3c763d");
                            $('#wkotp').removeClass("form-group has-error");
                            $('#wkotp').addClass("form-group has-success");
                            $(":submit").removeAttr("disabled").find('.fa-refresh').addClass('d-none');
                        } else {
                            $(":submit").attr("disabled", true);
                            $('#otp').after("<i class='fa fa-times-circle wkcheck' aria-hidden='true'></i>");
                            $('#wkotp').removeClass("form-group has-success");
                            $(".wkcheck").css("color", "#a94442");
                            $('#wkotp').addClass("form-group has-error");
                        }
                    });
            } else {
                $(":submit").attr("disabled", true);
                $(".wkcheck").remove();
                $('#wkotp').removeClass("form-group has-success");
                $('#wkotp').removeClass("form-group has-error");
                $('#wkotp').addClass("form-group");
            }
        });
    }

})