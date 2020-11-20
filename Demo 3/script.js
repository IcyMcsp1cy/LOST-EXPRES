// Attempting to create the sign in, attached to a div in the html
var signIn = new Vue({
    el: '#app',
    data: {
        username: 'Enter Username',
        input_username: '',
        password: 'Enter Password',
        input_password: '',
        loggedIn: false,

    },
    methods: {
        compareLogIn: function (){
            if(this.input_username == "Capstone" && this.input_password == "Password"){
                this.loggedIn = true;
            }
            // GOTTA ADD SOMETHING THAT DISPLAYS LIKE SUCCESS OR FAIL
            else{

            }
        }
    }
})