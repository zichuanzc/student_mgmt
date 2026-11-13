document.addEventListener("DOMContentLoaded", () => {
  if (getCurrentUser()) {
    window.location.href = "./index.html";
    return;
  }
  document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const res = await request("POST", "/v0/user/login", {
      form: { username: fd.get("username"), password: fd.get("password") },
    });
    if (!res.ok) {
      toast(res.msg, "error");
      return;
    }
    const u = res.data?.data;
    if (!u) {
      toast("登录响应异常", "error");
      return;
    }
    setCurrentUser({
      user_id: u.user_id,
      user_name: u.user_name,
      full_name: u.full_name,
      role_id: u.role_id,
      role_name: u.role_name,
    });
    setOperatorPassword(fd.get("password"));
    toast("登录成功", "success");
    setTimeout(() => {
      window.location.href = "./index.html";
    }, 400);
  });
});
