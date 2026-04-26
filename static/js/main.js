/**
 * SICEME - JavaScript Principal
 * Dashboard, Chart.js, html2canvas, Sidebar, Interactividad
 */
// No registramos globalmente para evitar conflictos, lo haremos por instancia
console.log("SICEME: main.js cargado v1.3");
if (typeof ChartDataLabels === 'undefined') {
    console.error("SICEME Error: ChartDataLabels no está cargado. Verifique la conexión a internet o el CDN.");
} else {
    console.log("SICEME: Plugin de etiquetas detectado correctamente.");
}

// ─── Sidebar Toggle ───
document.addEventListener('DOMContentLoaded', function () {
    const mobileToggle = document.getElementById('btn-mobile-toggle');
    const desktopToggle = document.getElementById('btn-sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const mainContent = document.querySelector('.main-content');

    // Toggle Móvil (Slide-in)
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function () {
            if (sidebar) sidebar.classList.toggle('show');
            if (overlay) overlay.classList.toggle('show');
        });
    }

    // Toggle Escritorio (Collapse)
    if (desktopToggle) {
        desktopToggle.addEventListener('click', function () {
            if (sidebar) sidebar.classList.toggle('collapsed');
            if (mainContent) mainContent.classList.toggle('sidebar-collapsed');
            
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebar-collapsed', isCollapsed);
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function () {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    // Cargar estado inicial (Escritorio)
    if (window.innerWidth > 992 && localStorage.getItem('sidebar-collapsed') === 'true') {
        if (sidebar) sidebar.classList.add('collapsed');
        if (mainContent) mainContent.classList.add('sidebar-collapsed');
    }

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert-siceme');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function () { alert.remove(); }, 500);
        }, 5000);
    });

    // Active nav link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    navLinks.forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/dashboard/' && currentPath === '/dashboard/') {
            link.classList.add('active');
        }
    });

    // Tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });
});


// ─── Dashboard Charts ───
function initDashboardCharts() {
    const anio = new Date().getFullYear();

    fetch(`/api/dashboard-data/?anio=${anio}&_=${new Date().getTime()}`)
        .then(response => response.json())
        .then(data => {
            // Gráfico de barras - Emergencias por mes
            const ctxBar = document.getElementById('chart-emergencias-mes');
            if (ctxBar) {
                new Chart(ctxBar.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: data.emergencias_mensual.labels,
                        datasets: [{
                            label: 'Emergencias',
                            data: data.emergencias_mensual.data,
                            backgroundColor: 'rgba(124, 58, 237, 0.7)',
                            borderColor: '#7C3AED',
                            borderWidth: 1,
                            borderRadius: 6,
                            maxBarThickness: 40,
                        }]
                    },
                    plugins: [ChartDataLabels],
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        layout: {
                            padding: { top: 20 }
                        },
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                display: true,
                                anchor: 'end',
                                align: 'top',
                                color: '#7C3AED',
                                font: { weight: 'bold', size: 12 },
                                offset: 2,
                                formatter: (val) => val > 0 ? val : ''
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grace: '20%', // Espacio extra arriba para que no se corte el número
                                ticks: { font: { size: 11 }, color: '#9CA3AF' },
                                grid: { color: '#F3F4F6' }
                            },
                            x: {
                                ticks: { font: { size: 11 }, color: '#9CA3AF' },
                                grid: { display: false }
                            }
                        }
                    }
                });
            }

            // Gráfico de Barras Verticales - Distribución por especialidad
            const ctxEspecialidad = document.getElementById('chart-especialidades');
            if (ctxEspecialidad) {
                const mesesNombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                const ahora = new Date();
                const mesActual = mesesNombres[ahora.getMonth()];
                const anioActual = ahora.getFullYear();
                
                const colors = [
                    '#440154', '#482878', '#3e4989', '#31688e', '#26828e',
                    '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725'
                ];

                // Actualizar botón de descarga para incluir mes y año
                const btnDescarga = ctxEspecialidad.closest('.chart-card').querySelector('button');
                if (btnDescarga) {
                    btnDescarga.setAttribute('onclick', `exportarGraficoImagen('chart-especialidades', 'distribucion_especialidades_${mesActual.toLowerCase()}_${anioActual}.png')`);
                }

                // Actualizar título dinámico
                const tituloCont = document.getElementById('contenedor-titulo-esp');
                if (tituloCont) {
                    tituloCont.innerHTML = `
                        <i class="bi bi-bar-chart-line-fill" style="color:var(--primary)"></i> 
                        Distribución de Pacientes por Especialidad (${mesActual} ${anioActual})<br>
                        <small style="font-size: 0.6em; color: #6B7280;">Total: ${data.por_especialidad.total} Pacientes Activos</small>
                    `;
                }

                new Chart(ctxEspecialidad.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: data.por_especialidad.labels,
                        datasets: [{
                            data: data.por_especialidad.data,
                            backgroundColor: colors.slice(0, data.por_especialidad.labels.length),
                            borderRadius: 6,
                            maxBarThickness: 50,
                        }]
                    },
                    plugins: [ChartDataLabels],
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        layout: {
                            padding: { top: 30, bottom: 20 }
                        },
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                display: true,
                                anchor: 'end',
                                align: 'top',
                                color: '#4B5563',
                                font: { weight: 'bold', size: 12 },
                                formatter: (val) => val > 0 ? val : ''
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grace: '15%',
                                ticks: { font: { size: 11 }, color: '#9CA3AF' },
                                grid: { color: '#F3F4F6', borderDash: [5, 5] }
                            },
                            x: {
                                ticks: {
                                    font: { size: 10 },
                                    color: '#4B5563',
                                    maxRotation: 45,
                                    minRotation: 45
                                },
                                grid: { display: false }
                            }
                        }
                    }
                });
            }

            // Gráfico barras horizontales - Top Médicos
            const ctxTop = document.getElementById('chart-top-medicos');
            if (ctxTop) {
                new Chart(ctxTop.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: data.top_medicos.labels,
                        datasets: [{
                            label: 'Pacientes',
                            data: data.top_medicos.data,
                            backgroundColor: 'rgba(59, 130, 246, 0.7)',
                            borderColor: '#3B82F6',
                            borderWidth: 1,
                            borderRadius: 6,
                        }]
                    },
                    plugins: [ChartDataLabels],
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        layout: {
                            padding: { right: 30 }
                        },
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                display: true,
                                anchor: 'end',
                                align: 'right',
                                color: '#3B82F6',
                                font: { weight: 'bold', size: 11 },
                                formatter: (val) => val > 0 ? val : ''
                            }
                        },
                        scales: {
                            x: {
                                beginAtZero: true,
                                grace: '20%',
                                ticks: { font: { size: 11 }, color: '#9CA3AF' },
                                grid: { color: '#F3F4F6' }
                            },
                            y: {
                                ticks: { font: { size: 11 }, color: '#9CA3AF' },
                                grid: { display: false }
                            }
                        }
                    }
                });
            }

            // Gráfico de Pacientes No Asistidos (por especialidad)
            const ctxNA = document.getElementById('chart-no-asistidos');
            if (ctxNA) {
                const mesesNombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                const mesActual = mesesNombres[new Date().getMonth()];
                const spanMes = document.getElementById('mes-actual-na');
                if (spanMes) spanMes.innerText = mesActual;

                // Actualizar botón de descarga para incluir el mes
                const btnDescarga = ctxNA.closest('.chart-card').querySelector('button');
                if (btnDescarga) {
                    btnDescarga.setAttribute('onclick', `exportarGraficoImagen('chart-no-asistidos', 'no_asistidos_por_especialidad_${mesActual.toLowerCase()}.png')`);
                }

                // Actualizar título dinámico
                const tituloNA = document.getElementById('contenedor-titulo-na');
                if (tituloNA) {
                    tituloNA.innerHTML = `
                        <i class="bi bi-person-x-fill" style="color:var(--danger)"></i> 
                        Pacientes no asistidos por especialidad (${mesActual} ${data.anio})
                    `;
                }

                new Chart(ctxNA.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: data.no_asistidos.labels,
                        datasets: [{
                            data: data.no_asistidos.data,
                            backgroundColor: 'rgba(239, 68, 68, 0.7)',
                            borderColor: '#EF4444',
                            borderWidth: 1,
                            borderRadius: 6,
                            maxBarThickness: 50,
                        }]
                    },
                    plugins: [ChartDataLabels],
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        layout: {
                            padding: { top: 25 }
                        },
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                display: true,
                                anchor: 'end',
                                align: 'top',
                                color: '#EF4444',
                                font: { weight: 'bold', size: 11 },
                                formatter: (val) => val > 0 ? val : ''
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grace: '15%',
                                ticks: { font: { size: 11 }, color: '#9CA3AF' },
                                grid: { color: '#F3F4F6' }
                            },
                            x: {
                                ticks: { font: { size: 10 }, color: '#9CA3AF' },
                                grid: { display: false }
                            }
                        }
                    }
                });
            }

            // Gráfico de barras - Ecosonogramas por mes
            const ctxEcoMes = document.getElementById('chart-ecosonogramas-mes');
            if (ctxEcoMes) {
                new Chart(ctxEcoMes.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: data.ecosonogramas_mensual.labels,
                        datasets: [{
                            label: 'Ecosonogramas',
                            data: data.ecosonogramas_mensual.data,
                            backgroundColor: 'rgba(16, 185, 129, 0.7)',
                            borderColor: '#10b981',
                            borderWidth: 1,
                            borderRadius: 6,
                            maxBarThickness: 40,
                        }]
                    },
                    plugins: [ChartDataLabels],
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        layout: { padding: { top: 20 } },
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                display: true, anchor: 'end', align: 'top',
                                color: '#14b8a6',
                                font: { weight: 'bold', size: 12 },
                                offset: 2,
                                formatter: (val) => val > 0 ? val : ''
                            }
                        },
                        scales: {
                            y: { beginAtZero: true, grace: '20%', ticks: { font: { size: 11 }, color: '#9CA3AF' }, grid: { color: '#F3F4F6' } },
                            x: { ticks: { font: { size: 11 }, color: '#9CA3AF' }, grid: { display: false } }
                        }
                    }
                });
            }

            // Gráfico de barras - Ecosonogramas por tipo
            const ctxEcoTipo = document.getElementById('chart-eco-tipo');
            if (ctxEcoTipo) {
                const mesesNombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                const ahora = new Date();
                const mesActual = mesesNombres[ahora.getMonth()];
                const anioActual = ahora.getFullYear();

                // Actualizar botón de descarga para incluir mes y año
                const btnDescarga = ctxEcoTipo.closest('.chart-card').querySelector('button');
                if (btnDescarga) {
                    btnDescarga.setAttribute('onclick', `exportarGraficoImagen('chart-eco-tipo', 'distribucion_tipos_eco_${mesActual.toLowerCase()}_${anioActual}.png')`);
                }

                const ecoColors = ['#10b981', '#059669', '#047857', '#065f46', '#064e3b', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5', '#ecfdf5'];
                const tituloEco = document.getElementById('contenedor-titulo-eco');
                if (tituloEco) {
                    tituloEco.innerHTML = `
                        <i class="bi bi-pie-chart-fill" style="color:#10b981"></i> 
                        Distribución por Tipo de Ecosonograma (${mesActual} ${anioActual})<br>
                        <small style="font-size: 0.6em; color: #6B7280;">Total: ${data.eco_por_tipo.total} Ecosonogramas Activos</small>
                    `;
                }
                new Chart(ctxEcoTipo.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: data.eco_por_tipo.labels,
                        datasets: [{
                            data: data.eco_por_tipo.data,
                            backgroundColor: ecoColors.slice(0, data.eco_por_tipo.labels.length),
                            borderRadius: 6, maxBarThickness: 50,
                        }]
                    },
                    plugins: [ChartDataLabels],
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        layout: { padding: { top: 30, bottom: 20 } },
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                display: true, anchor: 'end', align: 'top',
                                color: '#0d9488',
                                font: { weight: 'bold', size: 12 },
                                formatter: (val) => val > 0 ? val : ''
                            }
                        },
                        scales: {
                            y: { beginAtZero: true, grace: '15%', ticks: { font: { size: 11 }, color: '#9CA3AF' }, grid: { color: '#F3F4F6', borderDash: [5, 5] } },
                            x: { ticks: { font: { size: 10 }, color: '#4B5563', maxRotation: 45, minRotation: 45 }, grid: { display: false } }
                        }
                    }
                });
            }

            // ─── NUEVOS GRÁFICOS: VIGILANCIA CENTINELA ───
            if (data.vigilancia_centinela) {
                // 1. Proporción Centinela
                const ctxCentPro = document.getElementById('chart-centinela-proporcion');
                if (ctxCentPro) {
                    new Chart(ctxCentPro, {
                        type: 'doughnut',
                        data: {
                            labels: data.vigilancia_centinela.labels,
                            datasets: [{
                                data: data.vigilancia_centinela.data,
                                backgroundColor: ['#f97316', '#e2e8f0'],
                                borderColor: ['#f97316', '#cbd5e1'],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true, maintainAspectRatio: false,
                            plugins: {
                                legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
                                datalabels: {
                                    color: '#ffffff',
                                    font: { weight: 'bold', size: 12 },
                                    formatter: (value, ctx) => {
                                        let sum = 0;
                                        let dataArr = ctx.chart.data.datasets[0].data;
                                        dataArr.map(data => { sum += data; });
                                        let percentage = (value*100 / sum).toFixed(0)+"%";
                                        return value > 0 ? value + "\n(" + percentage + ")" : '';
                                    }
                                },
                                tooltip: { 
                                    callbacks: {
                                        label: function(context) {
                                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                            const val = context.raw;
                                            const perc = ((val/total) * 100).toFixed(1);
                                            return `${context.label}: ${val} (${perc}%)`;
                                        }
                                    }
                                }
                            },
                            cutout: '70%'
                        }
                    });
                }

                // 2. Tendencia Centinela
                const ctxCentTen = document.getElementById('chart-centinela-tendencia');
                if (ctxCentTen) {
                    new Chart(ctxCentTen, {
                        type: 'line',
                        data: {
                            labels: data.emergencias_mensual.labels, // Ene, Feb, etc.
                            datasets: [{
                                label: 'Casos Centinela',
                                data: data.vigilancia_centinela.mensual,
                                borderColor: '#ef4444',
                                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                borderWidth: 3,
                                fill: true,
                                tension: 0.4,
                                pointBackgroundColor: '#ef4444',
                                pointRadius: 4
                            }]
                        },
                        options: {
                            responsive: true, maintainAspectRatio: false,
                            plugins: { 
                                legend: { display: false },
                                datalabels: {
                                    align: 'top',
                                    anchor: 'end',
                                    color: '#ef4444',
                                    font: { weight: 'bold' },
                                    formatter: (val) => val > 0 ? 'Casos: ' + val : ''
                                }
                            },
                            scales: {
                                y: { beginAtZero: true, ticks: { stepSize: 1 }, grace: '20%' },
                                x: { grid: { display: false } }
                            }
                        }
                    });
                }
            }
        })
        .catch(err => console.error('Error cargando datos del dashboard:', err));
}


// ─── Exportar gráfico como imagen ───
function exportarGraficoImagen(canvasId, filename) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const container = canvas.closest('.chart-card');
    if (container && typeof html2canvas !== 'undefined') {
        html2canvas(container, {
            backgroundColor: '#FFFFFF',
            scale: 2,
        }).then(function (renderedCanvas) {
            const link = document.createElement('a');
            link.download = filename || 'grafico_siceme.png';
            link.href = renderedCanvas.toDataURL();
            link.click();
        });
    } else {
        // Fallback: exportar solo el canvas
        const link = document.createElement('a');
        link.download = filename || 'grafico_siceme.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    }
}


// ─── Confirmar eliminación ───
function confirmarEliminacion(form) {
    return confirm('¿Está seguro de que desea eliminar este registro? Esta acción no se puede deshacer.');
}
