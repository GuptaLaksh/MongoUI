document.getElementById("remove").onclick = function() {
    var node = document.getElementById("register");
    node.parentNode.removeChild(node);
}