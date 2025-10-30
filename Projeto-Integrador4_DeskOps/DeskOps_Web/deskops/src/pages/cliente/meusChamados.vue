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
                <td>{{ chamado.atualizado }}</td>
                <td>{{ chamado.id }}</td>
                <td>{{ chamado.titulo }}</td>
                <td>
                  <div class="tecnico-info">
                    <p>{{ chamado.tecnico }}</p>
                    <p class="tecnico-email">{{ chamado.email || chamado.tecnico.toLowerCase() + '@email.com' }}</p>
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

// Importando a instância personalizada do axios
import api from "@/services/api";  


interface Chamado {
  id: number
  atualizado: string
  titulo: string
  tecnico: string
  email?: string
  status: string
  prioridade: string
}

export default defineComponent({
  name: 'MeusChamados',
  components: {
    ClienteSidebar
  },
  setup() {
    const router = useRouter()
    const filtroStatus = ref('todos')
    const filtroPrioridade = ref('todos')
    const ordemExibicao = ref('recente')
    const pesquisa = ref('')

    const usuario = ref({
      nome: 'Lucas Santino',
      email: 'lucas@email.com'
    })

    const chamados = ref<Chamado[]>([])

    // Função para carregar os chamados
    const carregarChamados = async () => {
      try {
        const response = await api.get('chamados/')  // Usando a instância do axios com token JWT
        chamados.value = response.data
      } catch (error) {
        console.error('Erro ao carregar chamados:', error)
      }
    }

    onMounted(() => {
      carregarChamados()
    })

    const closeProfileMenu = () => {
      // Esta função será chamada no clique da página para fechar o menu de perfil
    }

    const goToChamadoDetalhado = (id: number) => {
      router.push({ path: '/cliente/chamado-detalhado', query: { id: id.toString() } })
    }

    const filtrados = computed(() => {
      return chamados.value.filter((c) => {
        const matchStatus = filtroStatus.value === 'todos' || c.status.toLowerCase() === filtroStatus.value.toLowerCase()
        const matchPrioridade = filtroPrioridade.value === 'todos' || c.prioridade.toLowerCase() === filtroPrioridade.value.toLowerCase()
        const matchPesquisa =
          c.titulo.toLowerCase().includes(pesquisa.value.toLowerCase()) ||
          c.tecnico.toLowerCase().includes(pesquisa.value.toLowerCase())
        return matchStatus && matchPrioridade && matchPesquisa
      })
    })

    const chamadosOrdenados = computed(() => {
      const chamadosFiltrados = [...filtrados.value]

      if (ordemExibicao.value === 'recente') {
        return chamadosFiltrados.sort((a, b) => {
          return new Date(b.atualizado.split(' ')[0].split('/').reverse().join('-')).getTime() - 
                 new Date(a.atualizado.split(' ')[0].split('/').reverse().join('-')).getTime()
        })
      } else {
        return chamadosFiltrados.sort((a, b) => {
          return new Date(a.atualizado.split(' ')[0].split('/').reverse().join('-')).getTime() - 
                 new Date(b.atualizado.split(' ')[0].split('/').reverse().join('-')).getTime()
        })
      }
    })

    const statusClass = (status: string) => {
      switch (status.toLowerCase()) {
        case 'concluído': return 'status-concluido'
        case 'aberto': return 'status-aberto'
        case 'aguardando': return 'status-aguardando'
        case 'em andamento': return 'status-andamento'
        case 'cancelado': return 'status-cancelado'
        default: return ''
      }
    }

    const statusIcon = (status: string) => {
      switch (status.toLowerCase()) {
        case 'concluído': return 'check_circle'
        case 'aberto': return 'circle'
        case 'aguardando': return 'hourglass_top'
        case 'em andamento': return 'autorenew'
        case 'cancelado': return 'cancel'
        default: return ''
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

