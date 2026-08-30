import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import MainLayout from "../components/layout/MainLayout.vue";
import Dashboard from "../views/Dashboard.vue";
import DataManager from "../views/DataManager.vue";
import TrackEvidence from "../views/TrackEvidence.vue";
import KnowledgeGraph from "../views/KnowledgeGraph.vue";
import FusionCandidates from "../views/FusionCandidates.vue";
import LLMDecision from "../views/LLMDecision.vue";
import ChatAssistant from "../views/ChatAssistant.vue";
import ExperimentResults from "../views/ExperimentResults.vue";
import YOLODetectionWorkbench from "../views/YOLODetectionWorkbench.vue";
import SystemSettings from "../views/SystemSettings.vue";

const routes = [
  { path: "/", redirect: "/dashboard" },
  { path: "/login", component: Login },
  {
    path: "/",
    component: MainLayout,
    children: [
      { path: "dashboard", component: Dashboard },
      { path: "data", component: DataManager },
      { path: "tracks", component: TrackEvidence },
      { path: "kg", component: KnowledgeGraph },
      { path: "fusion", component: FusionCandidates },
      { path: "llm-decision", component: LLMDecision },
      { path: "chat", component: ChatAssistant },
      { path: "experiments", component: ExperimentResults },
      { path: "yolo-detection", component: YOLODetectionWorkbench },
      { path: "settings", component: SystemSettings },
    ],
  },
];

const router = createRouter({ history: createWebHistory(), routes });
router.beforeEach((to) => {
  if (to.path !== "/login" && !localStorage.getItem("token")) return "/login";
});
export default router;
