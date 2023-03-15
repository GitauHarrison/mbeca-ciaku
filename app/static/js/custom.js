var myInput = document.getElementById("password");
var letter = document.getElementById("letter");
var capital = document.getElementById("capital");
var number = document.getElementById("number");
var length = document.getElementById("length");

var myInputRegisterPassword = document.getElementById("register_password");
var letter_register_password = document.getElementById("letter_register_password");
var capital_register_password = document.getElementById("capital_register_password");
var number_register_password = document.getElementById("number_register_password");
var length_register_password = document.getElementById("length_register_password");

var myInputRegisterConfirmPassword = document.getElementById("register_confirm_password");
var letter_register_confirm_password = document.getElementById("letter_register_confirm_password");
var capital_register_confirm_password = document.getElementById("capital_register_confirm_password");
var number_register_confirm_password = document.getElementById("number_register_confirm_password");
var length_register_confirm_password = document.getElementById("length_register_confirm_password");

// When the user clicks on the password field, show the message box
myInput.onfocus = function() {
  document.getElementById("message").style.display = "block";
}
myInputRegisterPassword.onfocus = function() {
    document.getElementById("register_password_message").style.display = "block";
}
myInputRegisterConfirmPassword.onfocus = function() {
    document.getElementById("register_confirm_password_message").style.display = "block";
}


// When the user clicks outside of the password field, hide the message box
myInput.onblur = function() {
  document.getElementById("message").style.display = "none";
}
myInputRegisterPassword.onblur = function() {
    document.getElementById("register_password_message").style.display = "none";
}
  myInputRegisterConfirmPassword.onblur = function() {
    document.getElementById("register_confirm_password_message").style.display = "none";
}


// When the user starts to type something inside the password field
myInput.onkeyup = function() {
  // Validate lowercase letters
  var lowerCaseLetters = /[a-z]/g;
  if(myInput.value.match(lowerCaseLetters)) {  
    letter.classList.remove("invalid");
    letter.classList.add("valid");
  } else {
    letter.classList.remove("valid");
    letter.classList.add("invalid");
  }
  
  // Validate capital letters
  var upperCaseLetters = /[A-Z]/g;
  if(myInput.value.match(upperCaseLetters)) {  
    capital.classList.remove("invalid");
    capital.classList.add("valid");
  } else {
    capital.classList.remove("valid");
    capital.classList.add("invalid");
  }

  // Validate numbers
  var numbers = /[0-9]/g;
  if(myInput.value.match(numbers)) {  
    number.classList.remove("invalid");
    number.classList.add("valid");
  } else {
    number.classList.remove("valid");
    number.classList.add("invalid");
  }
  
  // Validate length
  if(myInput.value.length >= 8) {
    length.classList.remove("invalid");
    length.classList.add("valid");
  } else {
    length.classList.remove("valid");
    length.classList.add("invalid");
  }
}


myInputRegisterPassword.onkeyup = function() {
    // Validate lowercase letters
    var lowerCaseLetters = /[a-z]/g;
    if(myInputRegisterPassword.value.match(lowerCaseLetters)) {  
        letter_register_password.classList.remove("invalid");
        letter_register_password.classList.add("valid");
    } else {
        letter_register_password.classList.remove("valid");
        letter_register_password.classList.add("invalid");
    }
    
    // Validate capital letters
    var upperCaseLetters = /[A-Z]/g;
    if(myInputRegisterPassword.value.match(upperCaseLetters)) {  
        capital_register_password.classList.remove("invalid");
        capital_register_password.classList.add("valid");
    } else {
        capital_register_password.classList.remove("valid");
        capital_register_password.classList.add("invalid");
    }
  
    // Validate numbers
    var numbers = /[0-9]/g;
    if(myInputRegisterPassword.value.match(numbers)) {  
        number_register_password.classList.remove("invalid");
        number_register_password.classList.add("valid");
    } else {
        number_register_password.classList.remove("valid");
        number_register_passwordber.classList.add("invalid");
    }
    
    // Validate length
    if(myInputRegisterPassword.value.length >= 8) {
        length_register_password.classList.remove("invalid");
        length_register_password.classList.add("valid");
    } else {
        length_register_password.classList.remove("valid");
        length_register_password.classList.add("invalid");
    }
}


myInputRegisterConfirmPassword.onkeyup = function() {
    // Validate lowercase letters
    var lowerCaseLetters = /[a-z]/g;
    if(myInputRegisterConfirmPassword.value.match(lowerCaseLetters)) {  
      letter_register_confirm_password.classList.remove("invalid");
      letter_register_confirm_password.classList.add("valid");
    } else {
      letter_register_confirm_password.classList.remove("valid");
      letter_register_confirm_password.classList.add("invalid");
    }
    
    // Validate capital letters
    var upperCaseLetters = /[A-Z]/g;
    if(myInputRegisterConfirmPassword.value.match(upperCaseLetters)) {  
      capital_register_confirm_password.classList.remove("invalid");
      capital_register_confirm_password.classList.add("valid");
    } else {
      capital_register_confirm_password.classList.remove("valid");
      capital_register_confirm_password.classList.add("invalid");
    }
  
    // Validate numbers
    var numbers = /[0-9]/g;
    if(myInputRegisterConfirmPassword.value.match(numbers)) {  
      number_register_confirm_password.classList.remove("invalid");
      number_register_confirm_password.classList.add("valid");
    } else {
      number_register_confirm_password.classList.remove("valid");
      number_register_confirm_password.classList.add("invalid");
    }
    
    // Validate length
    if(myInputRegisterConfirmPassword.value.length >= 8) {
      length_register_confirm_password.classList.remove("invalid");
      length_register_confirm_password.classList.add("valid");
    } else {
      length_register_confirm_password.classList.remove("valid");
      length_register_confirm_password.classList.add("invalid");
    }
}