<template>
  <div ref="el" class="chart large"></div>
</template>

<script setup>
import * as echarts from "echarts";
import { onMounted, ref, watch } from "vue";

const props = defineProps({ graph: Object });
const emit = defineEmits(["node-click"]);
const el = ref();
let chart;

function draw() {
  if (!chart) chart = echarts.init(el.value);
  const data = props.graph?.nodes || [];
  const links = props.graph?.edges || [];
  const categories = [...new Set(data.map((node) => node.type || "节点"))].map(
    (name) => ({ name }),
  );
  chart.setOption({
    tooltip: {
      formatter: (params) => {
        if (params.dataType === "edge") return params.data.relation || "关系";
        return `${params.data.name || params.data.id}<br/>${params.data.type || "节点"}<br/>${params.data.source || ""}`;
      },
    },
    legend: [
      {
        data: categories.map((item) => item.name).slice(0, 8),
        top: 0,
        type: "scroll",
      },
    ],
    series: [
      {
        type: "graph",
        layout: "force",
        roam: true,
        draggable: true,
        data: data.map((node) => ({
          ...node,
          category: node.type || "节点",
          symbolSize: node.type?.includes("轨迹") ? 46 : 30,
        })),
        links: links.map((edge) => ({ ...edge, lineStyle: { opacity: 0.38 } })),
        categories,
        label: {
          show: data.length <= 120,
          fontSize: 10,
          overflow: "truncate",
          width: 78,
        },
        emphasis: {
          focus: "adjacency",
          label: { show: true },
        },
        force: {
          repulsion: data.length > 200 ? 80 : 150,
          edgeLength: data.length > 200 ? 55 : 85,
          gravity: 0.08,
        },
      },
    ],
  });
  chart.off("click");
  chart.on("click", (params) => emit("node-click", params));
}

onMounted(draw);
watch(() => props.graph, draw, { deep: true });
</script>
