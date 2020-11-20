
// Attempting to create the sign in, attached to a div in the html
var signIn = new Vue({
  el: '#app',
  data: {
    username: 'Username',
    input_username: '',
    password: 'Password',
    input_password: '',
    loggedIn: false,

  },
  methods: {
    compareLoggIn: function (){

      var correct_username = this.input_username === "Capstone";
      var correct_password = this.input_password === "Password";

      // GOTTA ADD SOMETHING THAT DISPLAYS LIKE SUCCESS OR FAIL

      this.loggedIn = correct_password && correct_username;
    }
  }
})
