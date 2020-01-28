var current_clicked_token = '';

function getClickedToken(obj) {
    if (current_clicked_token !== "") {
            console.log(current_clicked_token)
    }

    current_clicked_token = obj.getAttribute("token")
    console.log(current_clicked_token)
    console.log(obj.hasAttribute('token'));

    var element = document.getElementById(current_clicked_token);
    element.classList.add("current");
    element.scrollIntoView({
                        behavior: "auto",
                        block:"center",
                        });
}