document.addEventListener("DOMContentLoaded", () => {
  const clock = document.querySelector("#live-clock");
  const chartContainer = document.querySelector("#sales-chart");
  const companyChartContainer = document.querySelector("#company-chart");
  const companyMonthChartContainer = document.querySelector("#company-month-chart");
  const statusPill = document.querySelector("#api-status");
  const API_BASE_URL =
    window.location.protocol.startsWith("http") && window.location.origin !== "null"
      ? window.location.origin
      : "http://127.0.0.1:5000";
  let chart;
  let companyChart;
  let companyMonthChart;
  let atualizacaoEmAndamento = false;
  const HORA_INICIO = 6;
  const HORA_FIM = 22;

  const getOperatingHours = () => {
    const horaAtual = new Date().getHours();
    const horaLimite = Math.min(Math.max(horaAtual, HORA_INICIO), HORA_FIM);
    return Array.from(
      { length: horaLimite - HORA_INICIO + 1 },
      (_, indice) => HORA_INICIO + indice
    );
  };

  const getVisibleChartData = (values) => {
    const horas = getOperatingHours();
    return {
      categorias: horas.map((hora) => `${String(hora).padStart(2, "0")}h`),
      valores: horas.map((hora) => Number(values?.[hora] || 0))
    };
  };

  const updateClock = () => {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");
    if (clock) {
      clock.textContent = `${hours}:${minutes}:${seconds}`;
    }
  };

  updateClock();
  setInterval(updateClock, 1000);

  chart = new ApexCharts(chartContainer, {
    chart: {
      type: "line",
      height: 400,
      background: "transparent",
      toolbar: { show: false },
      zoom: { enabled: false },
      foreColor: "#8b93a6"
    },
    series: [{ name: "Receita", data: getVisibleChartData(Array(24).fill(0)).valores }],
    colors: ["#3b82f6"],
    stroke: {
      curve: "straight",
      width: 4,
      lineCap: "butt",
      colors: ["#3b82f6"]
    },
    markers: {
      size: 4,
      strokeWidth: 2,
      strokeColors: "#ffffff",
      hover: { size: 6 },
      discrete: []
    },
    xaxis: {
      categories: getVisibleChartData(Array(24).fill(0)).categorias,
      labels: {
        style: { colors: "#8b93a6", fontSize: "11px" }
      },
      axisBorder: { show: false },
      axisTicks: { show: false }
    },
    yaxis: {
      min: 0,
      max: 200000,
      tickAmount: 5,
      labels: {
        formatter: (val) => `R$${(val / 1000).toFixed(1)}k`,
        style: { colors: "#8b93a6", fontSize: "11px" }
      }
    },
    grid: {
      show: true,
      borderColor: "rgba(255, 255, 255, 0.08)",
      strokeDashArray: 4,
      xaxis: { lines: { show: false } },
      yaxis: { lines: { show: true } }
    },
    tooltip: {
      theme: "dark",
      y: { formatter: (val) => `R$ ${val.toLocaleString("pt-BR")}` }
    },
    legend: { show: false }
  });

  chart.render();

  companyChart = new ApexCharts(companyChartContainer, {
    chart: {
      type: "bar",
      height: 400,
      background: "transparent",
      toolbar: { show: false },
      foreColor: "#8b93a6"
    },
    series: [{ name: "Faturamento", data: [] }],
    colors: ["#31557f"],
    plotOptions: {
      bar: {
        horizontal: true,
        borderRadius: 1,
        barHeight: "54%",
        dataLabels: { position: "end" }
      }
    },
    dataLabels: {
      enabled: true,
      textAnchor: "start",
      offsetX: 12,
      style: { colors: ["#ffffff"], fontSize: "10px", fontWeight: 600 },
      formatter: (val) => `R$ ${Number(val).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`
    },
    xaxis: {
      min: 0,
      tickAmount: 4,
      labels: {
        formatter: (val) => {
          if (val >= 1000000) return `R$ ${ (val / 1000000).toFixed(1) }M`;
          if (val >= 1000) return `R$ ${ (val / 1000).toFixed(1) }k`;
          return `R$ ${Number(val).toLocaleString("pt-BR")}`;
        },
        style: { colors: "#8b93a6", fontSize: "10px" },
        trim: false,
        hideOverlappingLabels: true
      },
      axisBorder: { show: false },
      axisTicks: { show: false }
    },
    yaxis: {
      labels: {
        maxWidth: 96,
        style: { colors: "#53677e", fontSize: "9px", fontWeight: 600 }
      }
    },
    grid: {
      borderColor: "rgba(83, 103, 126, 0.18)",
      strokeDashArray: 3,
      xaxis: { lines: { show: true } },
      yaxis: { lines: { show: false } }
    },
    tooltip: {
      y: { formatter: (val) => `R$ ${Number(val).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}` }
    },
    legend: { show: false }
  });

  companyChart.render();

  companyMonthChart = new ApexCharts(companyMonthChartContainer, {
    chart: {
      type: "bar",
      height: 400,
      background: "transparent",
      toolbar: { show: false },
      foreColor: "#8b93a6"
    },
    series: [{ name: "Faturamento Mês", data: [] }],
    colors: ["#0ea5e9"],
    plotOptions: {
      bar: {
        horizontal: true,
        borderRadius: 1,
        barHeight: "54%",
        dataLabels: { position: "end" }
      }
    },
    dataLabels: {
      enabled: true,
      textAnchor: "start",
      offsetX: 12,
      style: { colors: ["#ffffff"], fontSize: "10px", fontWeight: 600 },
      formatter: (val) => `R$ ${Number(val).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`
    },
    xaxis: {
      min: 0,
      tickAmount: 4,
      labels: {
        formatter: (val) => {
          if (val >= 1000000) return `R$ ${ (val / 1000000).toFixed(1) }M`;
          if (val >= 1000) return `R$ ${ (val / 1000).toFixed(1) }k`;
          return `R$ ${Number(val).toLocaleString("pt-BR")}`;
        },
        style: { colors: "#8b93a6", fontSize: "10px" },
        trim: false,
        hideOverlappingLabels: true
      },
      axisBorder: { show: false },
      axisTicks: { show: false }
    },
    yaxis: {
      labels: {
        maxWidth: 96,
        style: { colors: "#53677e", fontSize: "9px", fontWeight: 600 }
      }
    },
    grid: {
      borderColor: "rgba(83, 103, 126, 0.18)",
      strokeDashArray: 3,
      xaxis: { lines: { show: true } },
      yaxis: { lines: { show: false } }
    },
    tooltip: {
      y: { formatter: (val) => `R$ ${Number(val).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}` }
    },
    legend: { show: false }
  });

  companyMonthChart.render();

  const setCardValue = (id, value) => {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = value ?? "—";
    }
  };

  const applyDashboardData = (dados) => {
    const kpis = dados?.kpis || {};
    const grafico = dados?.grafico || {};

    setCardValue("card-total-vendido", kpis.total_vendido || "R$ 0,00");
    setCardValue("card-horario-pico", (kpis.horario_pico || "00:00").split(" ")[0]);
    setCardValue("card-horario-pico-sub", (kpis.horario_pico || "00:00").replace(/^\S+\s*/, "") || "sem dados");
    setCardValue("card-transacoes", kpis.transacoes || "0");
    setCardValue("card-ticket-medio", kpis.total_vendido_mes_atual || "R$ 0,00");
    setCardValue("card-mes-anterior", `Mês anterior: ${kpis.total_vendido_mes_anterior || "R$ 0,00"}`);

    const dadosVisiveis = getVisibleChartData(grafico.valores);
    chart.updateSeries([{ name: "Receita", data: dadosVisiveis.valores }]);
    chart.updateOptions({
      xaxis: { categories: dadosVisiveis.categorias },
      markers: {
        discrete: [{
          seriesIndex: 0,
          dataPointIndex: dadosVisiveis.valores.length - 1,
          fillColor: "#3b82f6",
          strokeColor: "#ffffff",
          size: 5
        }]
      }
    });

    const empresas = Array.isArray(dados.empresas) ? dados.empresas : [];
    companyChart.updateOptions({
      xaxis: { categories: empresas.map((empresa) => `${empresa.id} - ${empresa.nome}`) }
    });
    companyChart.updateSeries([
      { name: "Faturamento", data: empresas.map((empresa) => Number(empresa.valor || 0)) }
    ]);

    const empresasMes = Array.isArray(dados.empresas_mes) ? dados.empresas_mes : [];
    companyMonthChart.updateOptions({
      xaxis: { categories: empresasMes.map((empresa) => `${empresa.id} - ${empresa.nome}`) }
    });
    companyMonthChart.updateSeries([
      { name: "Faturamento Mês", data: empresasMes.map((empresa) => Number(empresa.valor || 0)) }
    ]);

    if (statusPill) {
      if (dados?.status === "cache") {
        statusPill.textContent = "● CACHE";
        statusPill.classList.remove("offline");
      } else {
        statusPill.textContent = "● AO VIVO";
        statusPill.classList.remove("offline");
      }
    }
  };

  async function atualizarDashboard() {
    if (atualizacaoEmAndamento) {
      return;
    }

    atualizacaoEmAndamento = true;
    let controller;
    let timeout;
    try {
      controller = new AbortController();
      timeout = setTimeout(() => controller.abort(), 8000);
      const resposta = await fetch(`${API_BASE_URL}/api/dashboard?ts=${Date.now()}`, {
        signal: controller.signal,
        cache: "no-store"
      });
      if (!resposta.ok) {
        throw new Error(`HTTP ${resposta.status}`);
      }

      const dados = await resposta.json();
      applyDashboardData(dados);
    } catch (erro) {
      console.warn("Aguardando conexão com a API...", erro);

      try {
        const cacheController = new AbortController();
        const cacheResposta = await fetch(`${API_BASE_URL}/cache_vendas.json?ts=${Date.now()}`, {
          signal: cacheController.signal,
          cache: "no-store"
        });
        if (cacheResposta.ok) {
          const cacheDados = await cacheResposta.json();
          applyDashboardData(cacheDados);
          return;
        }
      } catch (cacheErro) {
        console.warn("Falha ao carregar cache local:", cacheErro);
      }

      if (statusPill) {
        statusPill.textContent = "● OFFLINE";
        statusPill.classList.add("offline");
      }
      setCardValue("card-total-vendido", "R$ 0,00");
      setCardValue("card-horario-pico", "00:00");
      setCardValue("card-horario-pico-sub", "sem dados");
      setCardValue("card-transacoes", "0");
      setCardValue("card-ticket-medio", "N/D");
      const dadosVazios = getVisibleChartData(Array(24).fill(0));
      chart.updateSeries([{ name: "Receita", data: dadosVazios.valores }]);
      chart.updateOptions({
        xaxis: { categories: dadosVazios.categorias },
        markers: { discrete: [] }
      });
      companyChart.updateOptions({ xaxis: { categories: [] } });
      companyChart.updateSeries([{ name: "Faturamento", data: [] }]);
      companyMonthChart.updateOptions({ xaxis: { categories: [] } });
      companyMonthChart.updateSeries([{ name: "Faturamento Mês", data: [] }]);
    } finally {
      if (timeout) {
        clearTimeout(timeout);
      }
      atualizacaoEmAndamento = false;
    }
  }

  function agendarProximaAtualizacao() {
    setTimeout(async () => {
      await atualizarDashboard();
      agendarProximaAtualizacao();
    }, 5000);
  }

  atualizarDashboard();
  agendarProximaAtualizacao();
});
