import {
  getSession,
  isAuthConfigured,
  signInWithEmail,
  signInWithGoogle,
  signInWithMagicLink,
  signUpWithEmail,
} from "./auth.js";

const modal = document.getElementById("auth-modal");
const authError = document.getElementById("auth-error");
const enterBtn = document.getElementById("enter-btn");
const enterBtnHeader = document.getElementById("enter-btn-header");

function setError(message) {
  authError.textContent = message || "";
}

function openModal() {
  modal.classList.add("open");
  setError("");
}

function closeModal() {
  modal.classList.remove("open");
  setError("");
}

async function goToViewerIfAuthed() {
  const session = await getSession();
  if (session) {
    window.location.href = "viewer.html";
    return true;
  }
  return false;
}

async function openEntryFlow() {
  if (!isAuthConfigured()) {
    window.location.href = "viewer.html";
    return;
  }
  if (await goToViewerIfAuthed()) return;
  openModal();
}

enterBtn.addEventListener("click", openEntryFlow);
if (enterBtnHeader) enterBtnHeader.addEventListener("click", openEntryFlow);

document.getElementById("auth-close").addEventListener("click", closeModal);
modal.addEventListener("click", (event) => {
  if (event.target === modal) closeModal();
});

document.querySelectorAll(".auth-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".auth-tab").forEach((el) => el.classList.remove("active"));
    document.querySelectorAll(".auth-form").forEach((el) => el.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`form-${tab.dataset.tab}`).classList.add("active");
    setError("");
  });
});

document.getElementById("google-signin").addEventListener("click", async () => {
  try {
    setError("");
    await signInWithGoogle();
  } catch (error) {
    setError(error.message);
  }
});

document.getElementById("form-login").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    setError("");
    await signInWithEmail(
      document.getElementById("login-email").value.trim(),
      document.getElementById("login-password").value
    );
    window.location.href = "viewer.html";
  } catch (error) {
    setError(error.message);
  }
});

document.getElementById("form-signup").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    setError("");
    const result = await signUpWithEmail(
      document.getElementById("signup-email").value.trim(),
      document.getElementById("signup-password").value
    );
    if (result.session) {
      window.location.href = "viewer.html";
    } else {
      setError("Check your email to confirm your account.");
    }
  } catch (error) {
    setError(error.message);
  }
});

document.getElementById("form-magic").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    setError("");
    await signInWithMagicLink(document.getElementById("magic-email").value.trim());
    setError("Magic link sent — check your inbox.");
  } catch (error) {
    setError(error.message);
  }
});

goToViewerIfAuthed();

function initHeroScene() {
  const canvas = document.getElementById("hero-canvas");
  if (!window.THREE || !canvas) return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 0, 14);

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const group = new THREE.Group();
  scene.add(group);

  const nodeGeo = new THREE.SphereGeometry(0.07, 10, 10);
  const edgeGeo = new THREE.CylinderGeometry(0.018, 0.018, 1, 6);
  const nodeMat = new THREE.MeshBasicMaterial({ color: 0x3b9eff });
  const edgeMat = new THREE.MeshBasicMaterial({ color: 0x2ecc71, transparent: true, opacity: 0.45 });

  const nodes = [];
  for (let ring = 0; ring < 3; ring += 1) {
    const radius = 2.0 + ring * 1.3;
    const count = 6 + ring * 2;
    for (let i = 0; i < count; i += 1) {
      const angle = (i / count) * Math.PI * 2 + ring * 0.2;
      const y = (ring - 1) * 0.95;
      nodes.push(new THREE.Vector3(Math.cos(angle) * radius, y, Math.sin(angle) * radius));
    }
  }

  nodes.forEach((pos) => {
    const mesh = new THREE.Mesh(nodeGeo, nodeMat);
    mesh.position.copy(pos);
    group.add(mesh);
  });

  for (let i = 0; i < nodes.length; i += 1) {
    const a = nodes[i];
    const b = nodes[(i + 1) % nodes.length];
    const mid = a.clone().add(b).multiplyScalar(0.5);
    const len = a.distanceTo(b);
    const edge = new THREE.Mesh(edgeGeo, edgeMat);
    edge.scale.set(1, len, 1);
    edge.position.copy(mid);
    edge.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
    group.add(edge);
  }

  const innerRing = new THREE.Mesh(
    new THREE.TorusGeometry(2.6, 0.025, 6, 48),
    new THREE.MeshBasicMaterial({ color: 0xd4a017, transparent: true, opacity: 0.3 })
  );
  innerRing.rotation.x = Math.PI / 2;
  group.add(innerRing);

  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();
    group.rotation.y = t * 0.12;
    group.rotation.x = Math.sin(t * 0.2) * 0.08;
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

initHeroScene();
