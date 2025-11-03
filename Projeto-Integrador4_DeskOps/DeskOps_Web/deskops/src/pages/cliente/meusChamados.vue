<template>
  <div class="meus-chamados-page" @click="closeProfileMenu">
    <cliente-sidebar :usuario="usuario" />
    <main class="main-content">
      <div class="content-area">
        <h1 class="page-title">Meus Chamados</h1>

        <!-- Filtros -->
        <div class="filters">
          <select v-model="filtroStatus" class="filter-select">
            <option value="todos">Todos</option>
            <option value="concluido">Concluído</option>
            <option value="aberto">Aberto</option>
            <option value="aguardando">Aguardando</option>
            <option value="andamento">Em Andamento</option>
            <option value="cancelado">Cancelado</option>
          </select>

          <!-- Filtro de Prioridade -->
          <select v-model="filtroPrioridade" class="filter-select">
            <option value="todos">Todas as Prioridades</option>
            <option value="alta">Alta</option>
            <option value="media">Média</option>
            <option value="baixa">Baixa</option>
          </select>

          <!-- Filtro de Ordenação -->
          <select v-model="ordemExibicao" class="filter-select">
            <option value="recente">Mais recente</option>
            <option value="antigo">Mais antigo</option>
          </select>

          <input
            type="text"
            v-model="pesquisa"
            placeholder="Pesquisar por título ou técnico"
            class="filter-search"
          />
        </div>

        <!-- Tabela de chamados -->
        <div class="table-container">
          <table class="chamados-table">
            <thead>
              <tr>
                <th class="col-atualizado">Atualizado</th>
                <th class="col-id">ID</th>
                <th class="col-titulo">Título e Serviço</th>
                <th class="col-tecnico">Técnico</th>
                <th class="col-prioridade">Prioridade</th>
                <th class="col-status">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="chamado in chamadosOrdenados"
                :key="chamado.id"
                @click="goToChamadoDetalhado(chamado.id)"
                class="clickable-row"
              >
                <td>{{ chamado.update_date  }}</td>
                <td>{{ chamado.id }}</td>
                <td>{{ chamado.title }}</td>
                <td>
                  <div class="tecnico-info">
                    <p>{{ chamado.tecnico }}</p>
                   <p class="tecnico-email">
  {{ chamado.email || (chamado.tecnico ? chamado.tecnico.toLowerCase() + '@email.com' : 'sem-técnico') }}
</p>

                  </div>
                </td>
                <td>
                  <span :class="['prioridade', prioridadeClass(chamado.prioridade)]">
                    <span class="material-icons prioridade-icon">
                      {{ prioridadeIcon(chamado.prioridade) }}
                    </span>
                    {{ formatarPrioridade(chamado.prioridade) }}
                  </span>
                </td>
                <td>
                  <span :class="['status', statusClass(chamado.status)]">
                    <span class="material-icons status-icon">
                      {{ statusIcon(chamado.status) }}
                    </span>
                    {{ chamado.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ClienteSidebar from '@/components/layouts/clienteSidebar.vue'
import { useAuthStore } from '@/stores/authStore'
import api from '@/services/api' // axios configurado

interface Chamado {
  id: number
  title: string
  status: string
  prioridade: string
  update_date: string
  tecnico?: string
  email?: string
}

export default defineComponent({
  name: 'MeusChamados',
  components: { ClienteSidebar },

  setup() {
    const router = useRouter()
    const auth = useAuthStore()

    // 🔽 Filtros
    const filtroStatus = ref('todos')
    const filtroPrioridade = ref('todos')
    const ordemExibicao = ref('recente')
    const pesquisa = ref('')

    const usuario = ref({
      nome: auth.user?.name || 'Usuário',
      email: auth.user?.email || 'sem@email.com'
    })

    const chamados = ref<Chamado[]>([])

    // ✅ Função para carregar os chamados do usuário logado
    const carregarChamados = async () => {
      try {
        const token = auth.access
        if (!token) {
          console.warn("⚠️ Nenhum token encontrado. Redirecionando para login...")
          router.push('/')
          return
        }

        const response = await api.get('chamados/', {
          headers: { Authorization: `Bearer ${token}` }
        })

        console.log("📦 Dados recebidos:", response.data)

        chamados.value = (response.data.results || response.data).filter(
  (c: any) => c.creator === auth.user?.id
)


        // Se o backend retorna uma lista simples
        chamados.value = response.data.results || response.data
        console.log("✅ Chamados carregados:", chamados.value)
      } catch (error: any) {
        console.error("❌ Erro ao carregar chamados:", error.response?.data || error)
        if (error.response?.status === 401) {
          alert("Sessão expirada. Faça login novamente.")
          router.push('/')
        }
      }
    }

    // ✅ Executa ao carregar a página
    onMounted(() => {
      carregarChamados()
    })

    const closeProfileMenu = () => {}

   const goToChamadoDetalhado = (id: number) => {
  router.push({ name: 'ChamadoDetalhado', params: { id } })
}


    // ✅ Filtros dinâmicos
    const filtrados = computed(() => {
      return chamados.value.filter((c) => {
        const matchStatus =
          filtroStatus.value === 'todos' || c.status?.toLowerCase() === filtroStatus.value.toLowerCase()
        const matchPrioridade =
          filtroPrioridade.value === 'todos' || c.prioridade?.toLowerCase() === filtroPrioridade.value.toLowerCase()
        const matchPesquisa =
          c.title?.toLowerCase().includes(pesquisa.value.toLowerCase()) ||
          c.tecnico?.toLowerCase().includes(pesquisa.value.toLowerCase())
        return matchStatus && matchPrioridade && matchPesquisa
      })
    })

    // ✅ Ordenação (recente/antigo)
    const chamadosOrdenados = computed(() => {
      const lista = [...filtrados.value]
      if (ordemExibicao.value === 'recente') {
        return lista.sort((a, b) =>
          new Date(b.update_date).getTime() - new Date(a.update_date).getTime()
        )
      } else {
        return lista.sort((a, b) =>
          new Date(a.update_date).getTime() - new Date(b.update_date).getTime()
        )
      }
    })

    // ✅ Classes e ícones
    const statusClass = (status: string) => {
      switch (status.toLowerCase()) {
        case 'concluído': return 'status-concluido'
        case 'aberto': return 'status-aberto'
        case 'aguardando_atendimento': return 'status-aguardando'
        case 'em andamento': return 'status-andamento'
        case 'cancelado': return 'status-cancelado'
        default: return ''
      }
    }

    const statusIcon = (status: string) => {
      switch (status.toLowerCase()) {
        case 'concluído': return 'check_circle'
        case 'aberto': return 'circle'
        case 'aguardando_atendimento': return 'hourglass_top'
        case 'em andamento': return 'autorenew'
        case 'cancelado': return 'cancel'
        default: return 'help_outline'
      }
    }

    const prioridadeClass = (prioridade: string) => {
      switch (prioridade.toLowerCase()) {
        case 'alta': return 'prioridade-alta'
        case 'media': return 'prioridade-media'
        case 'baixa': return 'prioridade-baixa'
        default: return ''
      }
    }

    const prioridadeIcon = (prioridade: string) => {
      switch (prioridade.toLowerCase()) {
        case 'alta': return 'arrow_upward'
        case 'media': return 'remove'
        case 'baixa': return 'arrow_downward'
        default: return ''
      }
    }

    const formatarPrioridade = (prioridade: string) => {
      switch (prioridade.toLowerCase()) {
        case 'alta': return 'Alta Prioridade'
        case 'media': return 'Prioridade Média'
        case 'baixa': return 'Baixa Prioridade'
        default: return 'Sem Prioridade'
      }
    }

    return {
      filtroStatus,
      filtroPrioridade,
      ordemExibicao,
      pesquisa,
      usuario,
      chamados,
      carregarChamados,
      closeProfileMenu,
      goToChamadoDetalhado,
      filtrados,
      chamadosOrdenados,
      statusClass,
      statusIcon,
      prioridadeClass,
      prioridadeIcon,
      formatarPrioridade
    }
  }
})
</script>



<style scoped>
.meus-chamados-page {
  display: flex;
}

.main-content {
  flex-grow: 1;
  padding: 20px;
}

.page-title {
  font-size: 24px;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.filter-select, .filter-search {
  padding: 8px;
  margin-right: 10px;
  font-size: 14px;
}

.table-container {
  overflow-x: auto;
}

.chamados-table {
  width: 100%;
  border-collapse: collapse;
}

.chamados-table th, .chamados-table td {
  padding: 10px;
  text-align: left;
  border: 1px solid #ddd;
}

.clickable-row {
  cursor: pointer;
}

.status, .prioridade {
  display: flex;
  align-items: center;
}

.status-concluido { color: green; }
.status-aberto { color: blue; }
.status-aguardando { color: orange; }
.status-andamento { color: purple; }
.status-cancelado { color: red; }

.prioridade-alta { color: red; }
.prioridade-media { color: orange; }
.prioridade-baixa { color: green; }

.material-icons {
  margin-right: 5px;
}
</style>

