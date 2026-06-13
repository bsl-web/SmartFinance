document.addEventListener("DOMContentLoaded", () => {

    // =====================
    // GRÁFICO DE CATEGORIAS
    // =====================

    const categorias = window.categorias || {};
    
    const categoriaLabels = Object.keys(categorias);

    const categoriaValores = Object.values(categorias);

    const pizza = document.getElementById(
        "graficoCategorias"
    );

    if (pizza) {

        new Chart(pizza, {

            type: "pie",

            data: {

                labels: categoriaLabels,

                datasets: [{

                    data: categoriaValores,

                    backgroundColor: [

                        "#820ad1",
                        "#27ae60",
                        "#3498db",
                        "#f39c12",
                        "#e74c3c",
                        "#9b59b6"

                    ]

                }]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {

                        position: "bottom"

                    }

                }

            }

        });

    }

    // =====================
    // GRÁFICO MENSAL
    // =====================

    const meses = window.meses || [];

    const gastosMensais =
        window.gastosMensais || [];

    const linha = document.getElementById(
        "graficoMensal"
    );

    if (linha) {

        new Chart(linha, {

            type: "line",

            data: {

                labels: meses,

                datasets: [{

                    label: "Gastos Mensais",

                    data: gastosMensais,

                    borderColor: "#820ad1",

                    backgroundColor:
                    "rgba(130,10,209,.2)",

                    fill: true,

                    tension: .3

                }]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {

                        display: true

                    }

                }

            }

        });

    }

});