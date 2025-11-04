<template>
  <div class="gestao-ativos-page" @click="closeProfileMenu">
    <!-- Sidebar do Admin -->
    <adm-sidebar />

    <!-- Conteúdo principal -->
    <main class="main-content">
      <div class="content-area">
        <h1 class="page-title">Gestão de Ativos</h1>

        <!-- Filtros -->
        <div class="filters">
          <select v-model="filtroStatus" class="filter-select">
            <option value="todos">Todos os Status</option>
            <option value="ativo">Ativo</option>
            <option value="manutencao">Em Manutenção</option>
          </select>

          <select v-model="filtroAmbiente" class="filter-select">
            <option value="todos">Todos os Ambientes</option>
            <option v-for="ambiente in ambientes" :key="ambiente.id" :value="ambiente.id">
              {{ ambiente.nome }}
            </option>
          </select>

          <select v-model="ordemExibicao" class="filter-select">
            <option value="recente">Mais recente</option>
            <option value="antigo">Mais antigo</option>
            <option value="nome">Por nome</option>
          </select>

          <input
            type="text"
            v-model="pesquisa"
            placeholder="Pesquisar por nome ou descrição"
            class="filter-search"
          />

          <!-- Botão Cadastrar Ativo -->
          <button class="btn-cadastrar" @click="cadastrarAtivo">
            <span class="material-icons">add</span>
            Cadastrar Ativo
          </button>
        </div>

        <!-- Tabela de ativos -->
        <div class="table-container">
          <table class="ativos-table">
            <thead>
              <tr>
                <th class="col-id">ID</th>
                <th class="col-nome">Nome do Ativo</th>
                <th class="col-descricao">Descrição</th>
                <th class="col-ambiente">Ambiente</th>
                <th class="col-status">Status</th>
                <th class="col-qrcode">QR Code</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="ativo in ativosOrdenados"
                :key="ativo.id"
                @click="goToAtivoDetalhado(ativo.id)"
                class="clickable-row"
              >
                <td>{{ ativo.id }}</td>
                <td>
                  <p class="ativo-nome">{{ ativo.nome }}</p>
                </td>
                <td>
                  <p class="ativo-descricao">{{ ativo.descricao }}</p>
                </td>
                <td>
                  <div class="ambiente-info">
                    <p class="ambiente-nome">{{ ativo.ambiente.nome }}</p>
                    <p class="ambiente-local">{{ ativo.ambiente.localizacao }}</p>
                  </div>
                </td>
                <td>
                  <span :class="['status', statusClass(ativo.status)]">
                    <span class="material-icons status-icon">
                      {{ statusIcon(ativo.status) }}
                    </span>
                    {{ formatarStatus(ativo.status) }}
                  </span>
                </td>
                <td>
                  <span 
                    class="qr-code-available clickable-qr"
                    @click.stop="abrirModalQRCode(ativo)"
                  >
                    <span class="material-icons">qr_code_2</span>
                    Visualizar
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- Modal do QR Code -->
    <div v-if="modalAberto" class="modal-overlay" @click="fecharModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">QR Code do Ativo</h2>
          <button class="modal-close" @click="fecharModal">
            <span class="material-icons">close</span>
          </button>
        </div>

        <div class="modal-body">
          <!-- Informações do Ativo -->
          <div class="info-section">
            <h3 class="info-title">Informações do Ativo</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">ID:</span>
                <span class="info-value">{{ ativoSelecionado?.id }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Nome:</span>
                <span class="info-value">{{ ativoSelecionado?.nome }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Descrição:</span>
                <span class="info-value">{{ ativoSelecionado?.descricao }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Ambiente:</span>
                <span class="info-value">{{ ativoSelecionado?.ambiente.nome }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Localização:</span>
                <span class="info-value">{{ ativoSelecionado?.ambiente.localizacao }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Status:</span>
                <span :class="['info-value', statusClass(ativoSelecionado?.status || '')]">
                  {{ formatarStatus(ativoSelecionado?.status || '') }}
                </span>
              </div>
            </div>
          </div>

          <!-- QR Code -->
          <div class="qr-section">
            <h3 class="qr-title">Código QR</h3>
            <div class="qr-container">
              <div class="qr-code-wrapper">
                <qrcode-vue
                  :value="qrCodeValue"
                  :size="200"
                  level="H"
                  render-as="canvas"
                  class="qr-code"
                />
                <p class="qr-subtext">ID: {{ ativoSelecionado?.id }}</p>
              </div>
            </div>
            <div class="qr-actions">
              <button class="btn-download" @click="downloadQRCode">
                <span class="material-icons">download</span>
                Baixar QR Code
              </button>
              <button class="btn-print" @click="imprimirQRCode">
                <span class="material-icons">print</span>
                Imprimir
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdmSidebar from '@/components/layouts/admSidebar.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/authStore'

interface Ambiente {
  id: number
  nome: string
  localizacao: string
}

interface Ativo {
  id: number
  nome: string
  descricao: string
  ambiente: Ambiente
  status: string
  qrCode: string
  criadoEm: string
  atualizadoEm: string
}

export default defineComponent({
  name: 'DetalhesAtivos',
  components: { AdmSidebar },

  setup() {
    const route = useRoute()
    const router = useRouter()
    const auth = useAuthStore()
    const token = auth.access
    const ativoId = Number(route.params.id)

    const editando = ref(false)
    const carregando = ref(true)
    const ativo = ref<Ativo | null>(null)

    const formEdit = reactive({
      nome: '',
      descricao: '',
      ambiente: {
        id: 0,
        nome: '',
        localizacao: ''
      },
      status: ''
    })

    // 🔹 Usuário logado
    const usuario = ref({
      nome: 'Administrador',
      email: 'admin@deskops.com',
      tipoUsuario: 'Administrador',
      foto: '',
    })

    // 🔹 Buscar ativo da API
    const carregarAtivo = async () => {
      try {
        const response = await api.get(`/ativo/${ativoId}/`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        console.log('✅ Dados recebidos do ativo:', response.data)
        const a = response.data

        ativo.value = {
          id: a.id,
          nome: a.name,
          descricao: a.description || 'Sem descrição',
          ambiente: {
            id: a.environment?.id || 0,
            nome: a.environment?.name || 'Não definido',
            localizacao: a.environment?.localizacao || '---',
          },
          status: a.status || 'ativo',
          qrCode: a.qr_code || '---',
          criadoEm: a.created_at
            ? new Date(a.created_at).toLocaleString('pt-BR')
            : '---',
          atualizadoEm: a.updated_at
            ? new Date(a.updated_at).toLocaleString('pt-BR')
            : '---',
        }

        carregando.value = false
      } catch (error: any) {
  console.error('❌ Erro ao carregar ativo:', error)

  if (error.response) {
    console.error('🧩 Código HTTP:', error.response.status)
    console.error('🧩 Dados retornados:', error.response.data)
  } else if (error.request) {
    console.error('📡 Nenhuma resposta do servidor (erro de rede):', error.request)
  } else {
    console.error('⚙️ Erro na configuração da requisição:', error.message)
  }

  alert('Erro ao carregar dados do ativo.')
  router.push('/adm/gestao-ativos')
}

    }

    // 🔹 Iniciar edição
    const iniciarEdicao = () => {
      if (!ativo.value) return
      formEdit.nome = ativo.value.nome
      formEdit.descricao = ativo.value.descricao
      formEdit.ambiente = { ...ativo.value.ambiente }
      formEdit.status = ativo.value.status
      editando.value = true
    }

    // 🔹 Cancelar edição
    const cancelarEdicao = () => {
      editando.value = false
    }

    // 🔹 Salvar alterações na API
    const salvarEdicao = async () => {
      try {
        const payload = {
          name: formEdit.nome,
          description: formEdit.descricao,
          status: formEdit.status,
          environment: formEdit.ambiente.id,
        }

        await api.put(`/ativo/${ativoId}/`, payload, {
          headers: { Authorization: `Bearer ${token}` },
        })

        alert('✅ Alterações salvas com sucesso!')
        editando.value = false
        await carregarAtivo()
      } catch (error) {
        console.error('❌ Erro ao salvar ativo:', error)
        alert('Erro ao salvar alterações.')
      }
    }

    // 🔹 Alterar status do ativo
    const alterarStatus = async () => {
      try {
        const novoStatus = ativo.value?.status === 'ativo' ? 'manutencao' : 'ativo'

        await api.patch(`/ativo/${ativoId}/`, { status: novoStatus }, {
          headers: { Authorization: `Bearer ${token}` },
        })

        ativo.value!.status = novoStatus
        ativo.value!.atualizadoEm = new Date().toLocaleString('pt-BR')
        alert(`Ativo ${novoStatus === 'manutencao' ? 'colocado em manutenção' : 'reativado'} com sucesso!`)
      } catch (error) {
        console.error('❌ Erro ao alterar status do ativo:', error)
        alert('Erro ao alterar status.')
      }
    }

    // 🔹 Excluir ativo
    const excluirAtivo = async () => {
      if (!confirm('Tem certeza que deseja excluir este ativo?')) return

      try {
        await api.delete(`/ativo/${ativoId}/`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        alert('✅ Ativo excluído com sucesso!')
        router.push('/adm/gestao-ativos')
      } catch (error) {
        console.error('❌ Erro ao excluir ativo:', error)
        alert('Erro ao excluir ativo.')
      }
    }

    // 🔹 Utilitários visuais
    const closeProfileMenu = () => {}
    const statusClass = (status: string) => status === 'ativo' ? 'status-ativo' : 'status-manutencao'
    const statusIcon = (status: string) => status === 'ativo' ? 'check_circle' : 'build'
    const formatarStatus = (status: string) =>
      status === 'ativo' ? 'Ativo' : status === 'manutencao' ? 'Em Manutenção' : status

    onMounted(() => carregarAtivo())

    return {
      ativo,
      usuario,
      editando,
      carregando,
      formEdit,
      closeProfileMenu,
      statusClass,
      statusIcon,
      formatarStatus,
      alterarStatus,
      excluirAtivo,
      iniciarEdicao,
      cancelarEdicao,
      salvarEdicao,
    }
  },
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

/* RESET COMPLETO E FULLSCREEN */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Segoe UI', sans-serif;
}

html, body, #app {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

/* CONTAINER PRINCIPAL - FULLSCREEN */
.gestao-ativos-page {
  display: flex;
  height: 100vh;
  width: 100vw;
  min-height: 100vh;
  min-width: 100vw;
  overflow: hidden;
  background-color: #fff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* CONTEÚDO PRINCIPAL - ALTURA OTIMIZADA */
.main-content {
  flex: 1;
  background-color: #fff;
  margin-left: 250px;
  width: calc(100vw - 250px);
  height: 100vh;
  overflow: hidden;
  display: flex;
  justify-content: center;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  height: auto;
  min-height: 100vh;
  overflow: hidden;
  padding: 0 40px;
}

/* Cabeçalho - MAIS ESPAÇAMENTO SUPERIOR */
.page-title {
  color: indigo;
  font-size: 28px;
  font-weight: bold;
  padding: 50px 0 25px 0;
  background-color: #fff;
  margin: 0;
  width: 100%;
  text-align: left;
}

/* Filtros - Container com borda cinza e box-shadow */
.filters {
  display: flex;
  gap: 15px;
  padding: 15px 20px;
  background-color: #fff;
  width: 100%;
  align-items: center;
  max-width: 100%;
  border: 1px solid #d0d0d0;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-select,
.filter-search {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
  background-color: #fff;
  color: #000;
  transition: border-color 0.2s;
  height: 40px;
}

.filter-select {
  min-width: 140px;
  max-width: 160px;
}

.filter-search {
  flex: 1;
  min-width: 180px;
  max-width: 250px;
}

.filter-select:focus,
.filter-search:focus {
  outline: none;
  border-color: indigo;
}

/* Botão Cadastrar */
.btn-cadastrar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #000;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.2s;
  height: 40px;
  white-space: nowrap;
}

.btn-cadastrar:hover {
  background-color: #222;
  transform: translateY(-2px);
}

.btn-cadastrar .material-icons {
  font-size: 18px;
  color: #fff;
}

/* Container da Tabela - ALTURA OTIMIZADA */
.table-container {
  height: auto;
  min-height: 400px;
  max-height: calc(100vh - 300px);
  padding: 0;
  overflow: auto;
  background-color: #fff;
  max-width: 100%;
  border: 1px solid #d0d0d0;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

/* Tabela - Dimensões otimizadas */
.ativos-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  table-layout: fixed;
  min-width: 900px;
}

.ativos-table th,
.ativos-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  word-wrap: break-word;
  vertical-align: middle;
}

.ativos-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #333;
  position: sticky;
  top: 0;
  z-index: 10;
  border-bottom: 2px solid #d0d0d0;
  font-size: 13px;
}

.ativos-table td {
  color: #333;
  font-size: 13px;
}

.ativos-table tr:last-child td {
  border-bottom: none;
}

/* LARGURAS DAS COLUNAS OTIMIZADAS */
.col-id {
  width: 6%;
  min-width: 60px;
}

.col-nome {
  width: 20%;
  min-width: 150px;
}

.col-descricao {
  width: 30%;
  min-width: 200px;
}

.col-ambiente {
  width: 20%;
  min-width: 140px;
}

.col-status {
  width: 12%;
  min-width: 100px;
}

.col-qrcode {
  width: 12%;
  min-width: 100px;
}

/* Estilos para o conteúdo das células */
.ativo-nome {
  margin: 0;
  font-weight: 500;
  line-height: 1.3;
}

.ativo-descricao {
  margin: 0;
  line-height: 1.3;
  color: #666;
}

.ambiente-info {
  display: flex;
  flex-direction: column;
}

.ambiente-nome {
  font-weight: 500;
  margin: 0;
  line-height: 1.2;
}

.ambiente-local {
  font-size: 11px;
  color: #666;
  margin: 1px 0 0 0;
  line-height: 1.2;
}

/* Status - ESTILO COMPACTO */
.status {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
  font-size: 12px;
  white-space: nowrap;
}

.status-icon {
  font-size: 14px;
  flex-shrink: 0;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

/* CORES DOS STATUS PARA ATIVOS */
.status-ativo {
  background-color: #d1fae5;
  color: #065f46;
}

.status-manutencao {
  background-color: #fff3cd;
  color: #856404;
}

/* Indicador de QR Code - CORES NEUTRAS E ELEGANTES */
.qr-code-available {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
  font-size: 12px;
  white-space: nowrap;
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  transition: all 0.2s;
}

.qr-code-available.clickable-qr {
  cursor: pointer;
}

.qr-code-available.clickable-qr:hover {
  background-color: #e5e7eb;
  border-color: #9ca3af;
  transform: translateY(-1px);
}

.qr-code-available .material-icons {
  font-size: 14px;
  color: #6b7280;
}

/* Linha clicável */
.clickable-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.clickable-row:hover {
  background-color: #f8f9fa;
}

/* SCROLLBAR PERSONALIZADA */
.table-container::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.table-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* MODAL STYLES */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-title {
  color: #000;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background-color: #f5f5f5;
}

.modal-close .material-icons {
  font-size: 20px;
  color: #666;
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-section {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 20px;
}

.info-title {
  color: #000;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #000;
  font-weight: 500;
}

.qr-section {
  text-align: center;
}

.qr-title {
  color: #000;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.qr-container {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 40px;
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.qr-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.qr-icon {
  font-size: 80px;
  color: #d1d5db;
}

.qr-text {
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  margin: 0;
}

.qr-subtext {
  color: #6b7280;
  font-size: 12px;
  margin: 0;
}

.qr-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-download,
.btn-print {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-download {
  background-color: #000;
  color: #fff;
}

.btn-download:hover {
  background-color: #333;
}

.btn-print {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-print:hover {
  background-color: #e5e7eb;
}

/* QR Code */
.qr-code-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.qr-code {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 8px;
  background: white;
}

.qr-subtext {
  color: #6b7280;
  font-size: 12px;
  margin: 0;
  font-weight: 500;
}


/* RESPONSIVIDADE */
@media (max-width: 1024px) {
  .main-content {
    margin-left: 220px;
    width: calc(100vw - 220px);
  }
  
  .content-area {
    padding: 0 30px;
  }
  
  .page-title {
    padding: 40px 0 20px 0;
  }
  
  .filters {
    gap: 10px;
  }
  
  .filter-select {
    min-width: 120px;
    max-width: 140px;
  }
  
  .filter-search {
    min-width: 150px;
    max-width: 200px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .qr-actions {
    flex-direction: column;
  }
}

@media (max-width: 900px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-select,
  .filter-search {
    width: 100%;
    max-width: 100%;
  }
  
  .btn-cadastrar {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .gestao-ativos-page {
    flex-direction: column;
  }
  
  .main-content {
    width: 100%;
    margin-left: 0;
    height: auto;
    min-height: calc(100vh - 200px);
  }
  
  .content-area {
    height: auto;
    padding: 0 20px;
    min-height: auto;
  }
  
  .page-title {
    font-size: 24px;
    padding: 30px 0 15px 0;
  }
  
  .table-container {
    max-height: none;
    min-height: 300px;
  }

  .modal-content {
    margin: 20px;
    max-height: calc(100vh - 40px);
  }

  .modal-body {
    padding: 16px;
  }

  .qr-container {
    padding: 20px;
  }

  .qr-icon {
    font-size: 60px;
  }
}

/* Estilos para telas muito grandes */
@media (min-width: 1600px) {
  .content-area {
    max-width: 1400px;
  }
}
</style>