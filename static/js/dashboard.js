// SmartFinance Dashboard

console.log("SmartFinance carregado");

// Saudação automática
window.addEventListener("load", function () {

    const hora = new Date().getHours();

    let mensagem = "";

    if (hora < 12) {
        mensagem = "Bom dia!";
    }
    else if (hora < 18) {
        mensagem = "Boa tarde!";
    }
    else {
        mensagem = "Boa noite!";
    }

    console.log(mensagem);
});

// Confirma logout
function confirmarLogout() {

    return confirm(
        "Deseja realmente sair?"
    );
}