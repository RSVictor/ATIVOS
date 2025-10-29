import { defineStore } from "pinia";
import api from "../services/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    access: localStorage.getItem("access_token") || null,
    refresh: localStorage.getItem("refresh_token") || null,
  }),

  actions: {
    async login(email, password) {
      try {
        const response = await api.post("login/", { email, password });
        this.access = response.data.access;
        this.refresh = response.data.refresh;
        this.user = response.data.user;

        localStorage.setItem("access_token", this.access);
        localStorage.setItem("refresh_token", this.refresh);
        localStorage.setItem("user", JSON.stringify(this.user));
        return response.data;
      } catch (error) {
        throw error.response?.data || { detail: "Erro no login" };
      }
    },

    async logout() {
      try {
        await api.post("logout/", { refresh: this.refresh });
      } catch {
        // mesmo se der erro, limpa a sessão
      } finally {
        this.user = null;
        this.access = null;
        this.refresh = null;
        localStorage.clear();
      }
    },

    async fetchUser() {
      try {
        const response = await api.get("me/");
        this.user = response.data;
        localStorage.setItem("user", JSON.stringify(this.user));
      } catch (error) {
        console.error("Erro ao buscar usuário:", error);
      }
    },
  },
});
