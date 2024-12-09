<template>
  <BContainer>
    <BRow>
      <BCol sm="12">
        <h1>B&B - Viewer</h1>
        <hr />
      </BCol>
      <BCol sm="12">
        <BFormRadioGroup v-model="modelo">
          <BFormRadio name="modelo" id="padrao" :value="0">Default</BFormRadio>
          <BFormRadio name="modelo" id="mochila" :value="1">Knapsack</BFormRadio>
          <BFormRadio name="modelo" id="tsp" :value="2">TSP</BFormRadio>
        </BFormRadioGroup>
        <hr />
      </BCol>
      <div v-if="modelo === 0">
        <BCol sm="12">
          <div class="mb-3">
            <label for="customRange2" class="form-label">Variables: {{ variaveis }}</label>
            <BFormInput type="range" @change="attItens" min="2" max="3" v-model="variaveis" />
          </div>
          <hr />
        </BCol>
        <BCol sm="12">
          <BFormRadioGroup v-model="tipo">
            <BFormRadio name="tipo" id="min" value="min">Min</BFormRadio>
            <BFormRadio name="tipo" id="padrao" value="max">Max</BFormRadio>
          </BFormRadioGroup>
          <hr />
        </BCol>
        <BCol sm="12">
          <BRow>
            <BCol md="2">
              <h2>Restrictions</h2>
            </BCol>
            <BCol md="10">
              <BButton variant="success" @click="addRestricao">Add Restriction</BButton>
            </BCol>
          </BRow>
          <BTableSimple>
            <BThead>
              <BTr>
                <BTh class="text-center">#</BTh>
                <template v-for="i in parseInt(variaveis)" :key="i">
                  <BTh class="text-center">X{{ i }}</BTh>
                  <BTh class="text-center" v-if="i != variaveis"></BTh>
                </template>
                <BTh class="text-center">Condition</BTh>
                <BTh class="text-center">C</BTh>
                <BTh class="text-center"></BTh>
              </BTr>
            </BThead>
            <BTbody>
              <BTr v-for="(item, k) in itens" :key="k">
                <BTd class="text-center">{{ k + 1 }}</BTd>
                <template v-for="i in parseInt(variaveis)" :key="i">
                  <BTd>
                    <BFormInput
                      type="number"
                      v-model="item[`x${i}`]"
                      class="form-control text-center"
                    />
                  </BTd>
                  <BTd class="text-center" v-if="i != variaveis">+</BTd>
                </template>
                <BTd v-if="k != 0">
                  <BFormSelect v-model="item.cond" :options="optionSel" />
                </BTd>
                <BTd class="text-center" v-else>=</BTd>
                <BTd class="text-center" v-if="k == 0">FO</BTd>
                <BTd v-else>
                  <BFormInput type="number" v-model="item.value" class="form-control text-center" />
                </BTd>
                <BTd v-if="k != 0">
                  <BButton variant="danger" @click="removeRestricao(k)"> - </BButton>
                </BTd>
                <BTd v-else></BTd>
              </BTr>
            </BTbody>
          </BTableSimple>
          <BButton variant="primary" @click="processa(null)">Solve</BButton>
        </BCol>
      </div>
      <div v-if="modelo === 1">
        <BCol sm="12">
          <BRow class="mb-3">
            <BCol sm="2">
              <label for="capacidade">Capacity:</label>
            </BCol>
            <BCol sm="10">
              <BFormInput id="capacidade" type="number" v-model="capacidade" />
            </BCol>
          </BRow>
        </BCol>
        <div class="col-sm-12">
          <div class="row">
            <div class="col-md-2">
              <h2>Items</h2>
            </div>
            <div class="col-md-10">
              <BButton variant="success" @click="addRestricao"> Add Item </BButton>
            </div>
          </div>
          <BTableSimple>
            <BThead>
              <BTr>
                <BTh class="text-center">#</BTh>
                <BTh class="text-center">Value</BTh>
                <BTh class="text-center">Weight</BTh>
                <BTh class="text-center"></BTh>
              </BTr>
            </BThead>
            <BTbody>
              <BTr v-for="(item, k) in itens" :key="k">
                <BTd class="text-center">{{ k + 1 }}</BTd>
                <BTd>
                  <BFormInput type="number" v-model="item.valor" class="text-center" />
                </BTd>
                <BTd>
                  <BFormInput type="number" v-model="item.peso" class="text-center" />
                </BTd>
                <BTd v-if="k != 0">
                  <BButton variant="danger" @click="removeRestricao(k)"> - </BButton>
                </BTd>
                <BTd v-else></BTd>
              </BTr>
            </BTbody>
          </BTableSimple>
          <BButton variant="primary" @click="processaMochila">Solve</BButton>
        </div>
        <BCol sm="12"></BCol>
      </div>
      <div v-if="modelo === 2">
        <BCol sm="12">
          <div class="mb-3">
            <label for="customRange2" class="form-label">Table Size: {{ tabela }}</label>
            <BFormInput type="range" @change="attItens" min="3" max="6" v-model="tabela" />
          </div>
          <hr />
        </BCol>
        <BCol sm="12">
          <BRow>
            <BCol md="2">
              <h2>Table</h2>
            </BCol>
          </BRow>
          <BTableSimple>
            <BThead>
              <BTr>
                <BTh class="text-center"></BTh>
                <template v-for="i in parseInt(tabela)" :key="i">
                  <BTh class="text-center">X{{ i }}</BTh>
                </template>
              </BTr>
            </BThead>
            <BTbody>
              <BTr v-for="(item, k) in parseInt(tabela)" :key="k">
                <BTh class="text-center">X{{ k + 1 }}</BTh>
                <template v-for="(i, j) in parseInt(tabela)" :key="i">
                  <BTd>
                    <BFormInput
                      type="number"
                      v-model="itens[0][`x${item}${i}`]"
                      :disabled="j - 1 == k - 1"
                      class="text-center"
                    />
                  </BTd>
                </template>
              </BTr>
            </BTbody>
          </BTableSimple>
          <BButton variant="primary" @click="processaTSP">Solve</BButton>
        </BCol>
      </div>
    </BRow>
    <BRow>
      <BCol sm="12" class="mb-4 mt-4" v-if="treeData && treeData.tree">
        <div class="graph">
          <h3>Problem Description</h3>
          <div v-if="treeData.description">
            <p v-for="(line, index) in treeData.description" :key="index">{{ line }}</p>
          </div>
          <h3>Branch and Bound Tree View</h3>
          <h4 v-if="treeData.objective_value">Objective Value: {{ treeData.objective_value }}</h4>
          <h4>Number of Steps: {{ numSteps }}</h4>
          <div class="mb-2" ref="network" style="height: 500px; border: 1px solid lightgray"></div>
          <div>
            <div class="details">
              <h4>
                Node Details{{ selectedNode && selectedNode.id ? ': ' + selectedNode.id : '' }}
              </h4>
              <p v-if="selectedNode && selectedNode.details">
                <span v-html="selectedNode.details"></span>
              </p>
              <p v-else>No node selected</p>
            </div>

            <!-- Restrições aplicadas ao nó selecionado -->
            <div
              class="restrictions"
              v-if="
                selectedNode && selectedNode.restrictions && selectedNode.restrictions.length > 0
              "
            >
              <h4>Restrictions Applied</h4>
              <ul>
                <li v-for="(restriction, index) in selectedNode.restrictions" :key="index">
                  {{ restriction }}
                </li>
              </ul>
            </div>
            <div
              class="restrictions"
              :style="{
                display:
                  selectedNode &&
                  selectedNode.selected_edges &&
                  selectedNode.selected_edges.length > 0
                    ? ''
                    : 'none'
              }"
            >
              <h4>Path Edges</h4>
              <div
                class="mb-2"
                ref="pathNetwork"
                style="height: 500px; border: 1px solid lightgray"
              ></div>
            </div>
          </div>
          <!-- Verificação de disponibilidade do contêiner e dos dados -->
        </div>
      </BCol>
    </BRow>
    <BModal
      v-model="modal"
      title="Select Variable to Fix"
      cancel-title="Close"
      cancel-variant="danger"
      :ok-disabled="selectVariable === null"
      ok-title="Select"
      @ok="processa(selectVariable)"
    >
      <BFormRadioGroup id="variables" v-model="selectVariable" name="variables">
        <BFormRadio v-for="variable in fractionalVariables" :key="variable" :value="variable">
          {{ variable }} ({{ getVariableValue(variable) }})
        </BFormRadio>
      </BFormRadioGroup>
    </BModal>
  </BContainer>
</template>

<script>
import axios from 'axios'
import { Network } from 'vis-network'

export default {
  name: 'HomeView',
  data() {
    return {
      //visualizacao
      modal: false,
      optionSel: [
        { value: '=', text: '=' },
        { value: '<=', text: '<=' },
        { value: '>=', text: '>=' }
      ],
      treeData: null,
      selectedNode: null,
      maxObjectiveValueNode: null, // Armazenar o nó com a maior solução inteira
      isMaximization: false, // Define se o problema é de maximização ou minimização
      maxSoFarOverall: -Infinity, // Armazena o maior valor geral de SUP ou INF
      numSteps: 0, // Contador de nós (passos)
      //fimvisualizacao
      variaveis: 2,
      tabela: 5,
      modelo: 0,
      itens: [
        { x1: 5, x2: 8 },
        { x1: 1, x2: 1, cond: '<=', value: 6 },
        { x1: 5, x2: 9, cond: '<=', value: 45 }
      ], //[{}],
      tipo: 'max',
      host: location.hostname,
      //mochila
      capacidade: 0,
      partialTree: null,
      showPopup: false,
      fractionalVariables: [],
      selectVariable: null
    }
  },
  watch: {
    treeData(newValue) {
      if (newValue && newValue.tree) {
        this.numSteps = this.countNodesInJson(newValue.tree) // Contar nós no JSON
        this.$nextTick(() => {
          if (this.modelo < 2) {
            this.initNetworkOld() // Renderizar a árvore
          } else {
            this.initNetwork() // Renderizar a árvore
          }
        })
      }
    },
    modelo() {
      this.limpaModelo()
    },
    itens: {
      deep: true,
      handler: function () {
        this.attItens()
      }
    }
  },
  methods: {
    limpaModelo() {
      if (this.modelo === 2) {
        // Se for TSP
        this.tabela = 6 // Define tamanho da tabela como 6
        this.itens = [
          {
            x12: 10,
            x13: 15,
            x14: 73,
            x15: 12,
            x16: 9,
            x21: 8,
            x23: 37,
            x24: 28,
            x25: 3,
            x26: 14,
            x31: 24,
            x32: 31,
            x34: 10,
            x35: 7,
            x36: 13,
            x41: 69,
            x42: 27,
            x43: 15,
            x45: 31,
            x46: 47,
            x51: 11,
            x52: 5,
            x53: 17,
            x54: 9,
            x56: 19,
            x61: 6,
            x62: 17,
            x63: 23,
            x64: 14,
            x65: 20
          }
        ]
        this.treeData = null
      } else if (this.modelo === 0) {
        this.variaveis = 2
        ;(this.itens = [
          { x1: 5, x2: 8 },
          { x1: 1, x2: 1, cond: '<=', value: 6 },
          { x1: 5, x2: 9, cond: '<=', value: 45 }
        ]),
          (this.tipo = 'max')
        this.treeData = null
      } else if (this.modelo === 1) {
        // this.capacidade = 50
        // this.itens = [
        //   { valor: 70, peso: 31 },
        //   { valor: 20, peso: 10 },
        //   { valor: 39, peso: 20 },
        //   { valor: 37, peso: 19 },
        //   { valor: 7, peso: 4 },
        //   { valor: 5, peso: 3 },
        //   { valor: 10, peso: 6 },
        // ]
        this.capacidade = 10
        this.itens = [
          { peso: 2, valor: 40 },
          { peso: 3.14, valor: 50 },
          { peso: 1.98, valor: 100 },
          { peso: 5, valor: 95 },
          { peso: 3, valor: 30 }
        ]
        this.treeData = null
      }
    },
    addRestricao() {
      this.itens.push({})
    },
    removeRestricao(indice) {
      this.itens.splice(indice, 1)
    },
    async processa(chosenVariable = null) {
      const vars = Object.keys(this.itens[0]).sort()
      const objective_coeffs = vars.map((k) => this.itens[0][k])
      const maximize = this.tipo === 'max'
      this.isMaximization = maximize
      const constraints_coeffs = this.itens.slice(1).map((i) => vars.map((k) => parseFloat(i[k])))
      const constraints_ops = this.itens.slice(1).map((i) => i.cond)
      const constraints_rhs = this.itens.slice(1).map((i) => parseFloat(i.value))
      const variable_type = 'non_negative_integer'
      const data = {
        objective_coeffs,
        constraints_coeffs,
        constraints_ops,
        constraints_rhs,
        maximize,
        variable_type
      }

      if (chosenVariable) {
        if (this.partialTree) {
          data.partial_tree = this.partialTree
        }
        data.chosen_variable = chosenVariable
      }

      try {
        // Chamada POST com o JSON no corpo
        const response = await axios.post(
          `${import.meta.env.VITE_BACK_HOST}/interactive_branch_and_bound`,
          data
        )

        if (response.data.status === 'Fractional solution') {
          this.fractionalVariables = response.data.fractional_variables
          this.showPopup = true
        } else {
          this.showPopup = false
        }

        this.treeData = response.data
        this.partialTree = this.treeData.tree
        this.selectVariable = null
        this.selectedNode = null

        console.log('Data received from backend:', this.treeData) // Verificação de dados
      } catch (error) {
        console.error('Error fetching data from backend:', error)
      }
    },
    async processaMochila() {
      const objective_coeffs = this.itens.map((i) => parseFloat(i.valor))
      const maximize = true
      this.isMaximization = maximize
      const constraints_coeffs = this.itens.map((i) => parseFloat(i.peso))
      const variable_type = 'binary'
      const data = {
        objective_coeffs: objective_coeffs,
        constraints_coeffs: [constraints_coeffs],
        constraints_ops: ['<='],
        constraints_rhs: [parseFloat(this.capacidade)],
        maximize,
        variable_type
      }
      try {
        // Chamada POST com o JSON no corpo
        const response = await axios.post(`${import.meta.env.VITE_BACK_HOST}/branch_and_bound`, data)

        this.treeData = response.data
        this.selectedNode = null
        console.log('Data received from backend:', this.treeData) // Verificação de dados
      } catch (error) {
        console.error('Error fetching data from backend:', error)
      }
    },
    async processaTSP() {
      this.isMaximization = false // Sempre é minimização
      const matriz = []
      this.itens.map((i) => {
        for (let k = 1; k <= this.tabela; k++) {
          matriz.push([])
          for (let j = 1; j <= this.tabela; j++) {
            if (Object.keys(i).includes(`x${k}${j}`) && k != j) {
              matriz[k - 1].push(parseFloat(i[`x${k}${j}`]))
            } else {
              matriz[k - 1].push(9999)
            }
          }
        }
      })
      const data = {
        matriz
      }
      try {
        // Chamada POST com o JSON no corpo
        const response = await axios.post(`${import.meta.env.VITE_BACK_HOST}/tsp/branch_and_bound`, data)

        this.treeData = response.data
        this.selectedNode = null
        console.log('Data received from backend:', response.data) // Verificação de dados
      } catch (error) {
        console.error('Error fetching data from backend:', error)
      }
    },
    attItens() {
      if (this.modelo === 0) {
        this.itens.map((i, j) => {
          if (!Object.keys(i).includes('x1')) {
            i['x1'] = 0
          }
          if (!Object.keys(i).includes('x2')) {
            i['x2'] = 0
          }
          if (this.variaveis == 3 && !Object.keys(i).includes('x3')) {
            i['x3'] = 0
          }
          if (this.variaveis == 2 && Object.keys(i).includes('x3')) {
            delete i['x3']
          }
          if (j != 0 && !Object.keys(i).includes('cond')) {
            i['cond'] = '<='
          }
          if (j != 0 && !Object.keys(i).includes('value')) {
            i['value'] = 0
          }
        })
      } else if (this.modelo === 1) {
        this.itens.map((i) => {
          if (!Object.keys(i).includes('valor')) {
            i['valor'] = 0
          }
          if (!Object.keys(i).includes('peso')) {
            i['peso'] = 0
          }
        })
      } else if (this.modelo === 2) {
        this.items = this.itens.map((i) => {
          for (let k = 1; k <= this.tabela; k++) {
            for (let j = 1; j <= this.tabela; j++) {
              if (!Object.keys(i).includes(`x${k}${j}`) && k != j) {
                i[`x${k}${j}`] = 0
              }
            }
          }
          for (let k = 1; k <= 6; k++) {
            for (let j = 1; j <= 6; j++) {
              if (Object.keys(i).includes(`x${k}${j}`) && (k > this.tabela || j > this.tabela)) {
                delete i[`x${k}${j}`]
              }
            }
          }
        })
      }
    },
    getVariableValue(variable) {
      if (!this.treeData || !this.treeData.tree || !this.treeData.tree.solution) {
        return ''
      }
      const index = parseInt(variable.replace('x', '')) - 1
      const value = this.treeData.tree.solution[index]
      return typeof value === 'number' ? value.toFixed(2) : value
    },
    getFractionalVariables(solution) {
      if (!solution || !Array.isArray(solution)) {
        return []
      }
      return solution.filter((value) => typeof value === 'number' && !Number.isInteger(value))
    },
    initNetworkOld() {
      if (this.$refs.network && this.treeData && this.treeData.tree) {
        const container = this.$refs.network
        const data = this.transformTreeDataOld(this.treeData.tree)

        const options = {
          groups: {
            maxSolutionNode: {
              color: { background: '#66BB6A', border: '#2E7D32' },
              shape: 'ellipse',
              font: {
                color: 'white',
                multi: true
              },
              borderWidth: 3,
              borderWidthSelected: 3,
              chosen: {
                node: (values) => {
                  values.color = '#66BB6A'
                  values.borderColor = '#2E7D32'
                }
              }
            },
            redNode: {
              color: { background: '#e57373', border: '#d32f2f' },
              shape: 'ellipse',
              font: { color: 'white' }
            },
            yellowNode: {
              color: { background: '#FFEB3B', border: '#FBC02D' },
              shape: 'ellipse',
              font: { color: 'black' }
            },
            defaultNode: {
              color: { background: '#97C2FC', border: '#2B7CE9' },
              shape: 'ellipse',
              font: { color: 'black' }
            }
          },
          layout: {
            hierarchical: false
          },
          physics: false
        }

        const network = new Network(container, data, options)

        network.on('hoverNode', (params) => {
          const nodeId = params.node
          const nodeData = data.nodes.find((node) => node.id === nodeId)
          this.selectedNode = { ...nodeData, id: nodeId }
        })

        network.on('blurNode', () => {
          this.selectedNode = null
        })

        network.on('click', (params) => {
          if (params.nodes.length > 0) {
            const nodeId = params.nodes[0]
            const nodeData = data.nodes.find((node) => node.id === nodeId)
            this.selectedNode = { ...nodeData, id: nodeId }

            if (nodeData.solution && Array.isArray(nodeData.solution)) {
              const fractionalVars = this.getFractionalVariables(nodeData.solution)
              if (fractionalVars.length >= 2) {
                this.fractionalVariables = fractionalVars.map((_, index) => `x${index + 1}`)
                if (this.modelo === 0) {
                  this.modal = true
                }
              }
            } else {
              this.fractionalVariables = []
              if (this.modelo === 0) {
                this.modal = false
              }
            }
          } else {
            this.selectedNode = null
            this.fractionalVariables = []
            if (this.modelo === 0) {
              this.modal = false
            }
          }
        })
      } else {
        console.error(
          'Error initializing network: Data tree or network container is not available.'
        )
      }
    },
    initNetwork() {
      if (this.$refs.network && this.treeData && this.treeData.tree) {
        const container = this.$refs.network
        const data = this.transformTreeData(this.treeData.tree)

        // Adiciona os estilos para diferentes tipos de nós
        const options = {
          groups: {
            maxSolutionNode: {
              color: { background: '#66BB6A', border: '#2E7D32' },
              shape: 'ellipse',
              font: {
                color: 'white',
                multi: true // Permitir múltiplas linhas de texto no rótulo
              },
              borderWidth: 3,
              borderWidthSelected: 3, // Mesmo estilo quando selecionado
              chosen: {
                node: (values) => {
                  values.color = '#66BB6A' // Manter verde quando selecionado
                  values.borderColor = '#2E7D32' // Manter a borda verde escura
                }
              }
            },
            redNode: {
              color: { background: '#e57373', border: '#d32f2f' },
              shape: 'ellipse',
              font: { color: 'white' }
            },
            yellowNode: {
              color: { background: '#FFEB3B', border: '#FBC02D' },
              shape: 'ellipse',
              font: { color: 'black' }
            },
            defaultNode: {
              color: { background: '#97C2FC', border: '#2B7CE9' },
              shape: 'ellipse',
              font: { color: 'black' }
            }
          },
          layout: {
            hierarchical: false // Desabilitar o layout hierárquico automático
          },
          physics: false // Desativar física para manter a árvore estática
        }

        const network = new Network(container, data, options)

        network.on('hoverNode', (params) => {
          const nodeId = params.node
          const nodeData = data.nodes.find((node) => node.id === nodeId)
          this.selectedNode = { ...nodeData, id: nodeId }
        })

        network.on('blurNode', () => {
          this.selectedNode = null
        })

        network.on('click', (params) => {
          if (params.nodes.length > 0) {
            const nodeId = params.nodes[0]
            const nodeData = data.nodes.find((node) => node.id === nodeId)
            this.selectedNode = { ...nodeData, id: nodeId }
            this.initPath()
          } else {
            this.selectedNode = null
          }
        })
      } else {
        console.error(
          'Error initializing network: Data tree or network container is not available.'
        )
      }
    },
    initPath() {
      if (this.$refs.pathNetwork && this.selectedNode && this.selectedNode.selected_edges) {
        const container = this.$refs.pathNetwork
        const nodes = []
        const edges = []
        for (let i = 0; i < this.tabela; i++) {
          nodes.push({
            id: i + 1,
            label: `${i + 1}`,
            group: 'defaultNode'
          })
        }
        this.selectedNode.selected_edges.forEach((edge) => {
          edges.push({
            from: edge[0],
            to: edge[1],
            label: `${edge[2]}`,
            arrows: {
              to: { enabled: true }
            }
          })
        })
        const data = { nodes, edges }

        // Adiciona os estilos para diferentes tipos de nós
        const options = {
          groups: {
            defaultNode: {
              color: { background: '#97C2FC', border: '#2B7CE9' },
              shape: 'ellipse',
              font: { color: 'black' }
            }
          }
          // layout: {
          //   hierarchical: false // Desabilitar o layout hierárquico automático
          // },
          // physics: false // Desativar física para manter a árvore estática
        }
        new Network(container, data, options)
      } else {
        console.error(
          'Error initializing network: Data tree or network container is not available.',
          this.$refs
        )
      }
    },
    isSupOrInfNodeOld(branch) {
      const objectiveValue = branch.objective_value

      // Verificar se a função objetivo e as variáveis da solução são inteiras
      const areSolutionValuesInteger =
        branch.solution && branch.solution.every((v) => Number.isInteger(v))
      const isObjectiveValueInteger = Number.isInteger(objectiveValue)

      // Apenas nós com função objetivo e variáveis inteiras podem ser SUP ou INF
      if (!areSolutionValuesInteger || !isObjectiveValueInteger) return false

      if (this.isMaximization) {
        // Atualizar o valor de maxSoFarOverall apenas se ambos forem inteiros
        if (objectiveValue > this.maxSoFarOverall) {
          this.maxSoFarOverall = objectiveValue
          return 'SUP'
        }
      } else {
        // Atualizar o valor de maxSoFarOverall apenas se ambos forem inteiros
        if (objectiveValue < this.maxSoFarOverall) {
          this.maxSoFarOverall = objectiveValue
          return 'INF'
        }
      }

      return false
    },
    // Função para determinar se o nó é SUP ou INF dependendo do tipo de problema
    isSupOrInfNode(branch) {
      const objectiveValue = branch.objective_value

      // Verificar se a função objetivo e as variáveis da solução são inteiras
      const areSolutionValuesInteger =
        branch.solution && branch.solution.every((v) => Number.isInteger(v))
      const isObjectiveValueInteger = Number.isInteger(objectiveValue)

      // Se solucao_completa não existir, considera como true
      const isSolucaoCompleta =
        branch.solucao_completa === undefined ? true : branch.solucao_completa

      // Apenas nós com função objetivo e variáveis inteiras E solução completa podem ser SUP ou INF
      if (!areSolutionValuesInteger || !isObjectiveValueInteger || !isSolucaoCompleta) return false

      if (this.isMaximization) {
        // Atualizar o valor de maxSoFarOverall apenas se ambos forem inteiros e solução for completa
        if (objectiveValue > this.maxSoFarOverall) {
          this.maxSoFarOverall = objectiveValue
          return 'SUP'
        }
      } else {
        // Atualizar o valor de maxSoFarOverall apenas se ambos forem inteiros e solução for completa
        if (objectiveValue < this.maxSoFarOverall) {
          this.maxSoFarOverall = objectiveValue
          return 'INF'
        }
      }

      return false
    },
    // Função para identificar se deve ser pintado de vermelho sem alterar o texto
    shouldPaintRed(branch) {
      const objectiveValue = branch.objective_value

      // O nó deve ser pintado de vermelho se for folha e seu valor for menor que o maior SUP anterior (no caso de maximização)
      if (
        branch.branches.length === 0 &&
        this.isMaximization &&
        objectiveValue < this.maxSoFarOverall
      ) {
        return true
      }
      return false
    },
    transformTreeDataOld(tree) {
      const nodes = []
      const edges = []

      this.maxSoFarOverall = this.isMaximization ? -Infinity : Infinity
      let optNode = null

      const xSpacing = 150
      const ySpacing = 100
      const displacement = 1.5

      let nodeCounter = 1

      const parseBranchOld = (branch, parentId = null, depth = 0, xPosition = 0) => {
        const id = nodeCounter++

        let label = ''
        let details = ''
        let restrictions = []
        let group = 'defaultNode'
        let solution = null
        let objectiveValue = null

        if (branch.podado || branch.solution === null) {
          label = `ID: ${id} \n INV`
          details = 'Unviable or pruned solution'
          group = 'redNode'
        } else {
          solution = branch.solution
          objectiveValue = branch.objective_value
          const areSolutionValuesInteger = solution.every((v) => Number.isInteger(v))
          const isObjectiveValueInteger = Number.isInteger(objectiveValue)

          const variables = solution
            .map((v) => (typeof v === 'number' ? v.toFixed(2) : v))
            .join(', ')

          if (areSolutionValuesInteger && isObjectiveValueInteger) {
            const supOrInf = this.isSupOrInfNodeOld(branch)

            if (supOrInf) {
              label = `ID: ${id}\n${objectiveValue} (${variables})\n[${supOrInf}]`
              group = 'yellowNode'

              if (
                !optNode ||
                (this.isMaximization && objectiveValue > optNode.objective_value) ||
                (!this.isMaximization && objectiveValue < optNode.objective_value)
              ) {
                optNode = { id, objective_value: objectiveValue }
              }

              if (this.isMaximization && objectiveValue > this.maxSoFarOverall) {
                this.maxSoFarOverall = objectiveValue
              } else if (!this.isMaximization && objectiveValue < this.maxSoFarOverall) {
                this.maxSoFarOverall = objectiveValue
              }
            } else {
              label = `ID: ${id}\n ${objectiveValue} (${variables})`
              if (this.shouldPaintRed(branch)) {
                group = 'redNode'
              }
            }
          } else {
            label = `ID: ${id} \n ${objectiveValue} (${variables})`
          }

          details = `Objective Function: ${objectiveValue}<br>Variables: (${variables})`
        }

        if (branch.bounds && branch.bounds.length > 0) {
          branch.bounds.forEach((bound, index) => {
            const lowerBound = bound[0] !== null ? bound[0] : '-∞'
            const upperBound = bound[1] !== null ? bound[1] : '+∞'
            restrictions.push(`${lowerBound} <= x${index + 1} <= ${upperBound}`)
          })
        }

        const xPos = xPosition * xSpacing
        const yPos = depth * ySpacing

        nodes.push({
          id,
          label,
          details,
          restrictions,
          x: xPos,
          y: yPos,
          group,
          solution,
          objective_value: objectiveValue
        })

        if (parentId !== null) {
          edges.push({
            from: parentId,
            to: id,
            label: branch.fixed_variable || ''
          })
        }

        if (branch.branches && branch.branches.length > 0) {
          let currentXPos = xPosition
          branch.branches.forEach((subBranch, index) => {
            const subXPos = currentXPos + (index === 0 ? -displacement : displacement)
            parseBranchOld(subBranch, id, depth + 1, subXPos)
          })
        }
      }

      parseBranchOld(tree, null, 0, 0)

      if (optNode) {
        nodes.forEach((node) => {
          if (node.id === optNode.id) {
            node.group = 'maxSolutionNode'
            node.label = node.label.replace(/\[SUP\]|\[INF\]/g, '')
            node.label += '[OPT]'
          }
        })
      }

      this.adjustNodePositions(nodes, xSpacing)

      return { nodes, edges }
    },
    transformTreeData(tree) {
      const nodes = []
      const edges = []
      this.maxSoFarOverall = this.isMaximization ? -Infinity : Infinity // Resetar o máximo ou mínimo geral
      let optNode = null // Armazenar o nó que será marcado como OPT

      // Definir espaçamento entre os nós
      const xSpacing = 150 // Espaçamento horizontal
      const ySpacing = 100 // Espaçamento vertical
      const displacement = 1.5 // Definir o valor de deslocamento para os nós filhos

      // Função para percorrer a árvore e centralizar os nós filhos em relação ao pai
      const parseBranch = (branch, parentId = null, depth = 0, xPosition = 0) => {
        const { id, objective_value, solution, podado, bounds, fixed_variable } = branch
        let label = `ID=${id}\n`
        let details = ''
        let restrictions = []

        let group = 'defaultNode' // Grupo padrão

        if (podado || solution === null) {
          label += 'INV' // Exibe INV para soluções inviáveis ou podadas
          details = 'Unviable or pruned solution'
          group = 'redNode' // Pinta o nó de vermelho
        } else {
          // Verificar se a função objetivo e as variáveis da solução são inteiras
          const areSolutionValuesInteger = solution.every((v) => Number.isInteger(v))
          const isObjectiveValueInteger = Number.isInteger(objective_value)

          // Exibir o valor da função objetivo seguido dos valores das variáveis (x1, x2, ...)
          const variables = solution.join(', ')

          if (areSolutionValuesInteger && isObjectiveValueInteger) {
            const supOrInf = this.isSupOrInfNode(branch)
            if (supOrInf) {
              // Exibir o rótulo "SUP" ou "INF" em uma nova linha
              label += `${objective_value}\n(${variables})\n[${supOrInf}]`
              group = 'yellowNode' // Pinta de amarelo para nós SUP ou INF

              // Identificar o maior SUP (maximização) ou menor INF (minimização)
              if (this.isMaximization && supOrInf === 'SUP') {
                if (!optNode || objective_value > optNode.objective_value) {
                  optNode = branch
                }
              } else if (!this.isMaximization && supOrInf === 'INF') {
                if (!optNode || objective_value < optNode.objective_value) {
                  optNode = branch
                }
              }
            } else {
              label += `${objective_value}\n(${variables})` // Exibe o valor da função objetivo e os valores das variáveis
              if (this.shouldPaintRed(branch)) {
                group = 'redNode' // Pinta o nó de vermelho sem alterar o texto
              }
            }
          } else {
            label += `${objective_value}\n(${variables})` // Exibe o valor da função objetivo e os valores das variáveis
          }

          details = `Objective Function: ${objective_value}<br>Variables: (${variables})`
        }

        if (bounds && bounds.length > 0) {
          bounds.forEach((bound, index) => {
            const lowerBound = bound[0] !== null ? bound[0] : '-∞'
            const upperBound = bound[1] !== null ? bound[1] : '+∞'
            restrictions.push(`${lowerBound} <= x${index + 1}   <= ${upperBound}`)
          })
        }

        // Definir a posição X e Y do nó
        const xPos = xPosition * xSpacing
        const yPos = depth * ySpacing
        const selected_edges = []

        solution.forEach((value, index) => {
          if (index < solution.length - 1) {
            selected_edges.push([
              value,
              solution[index + 1],
              this.itens[0][`x${value}${solution[index + 1]}`]
            ])
          } else {
            selected_edges.push([value, solution[0], this.itens[0][`x${value}${solution[0]}`]])
          }
        })

        nodes.push({
          id,
          label,
          details,
          restrictions,
          selected_edges,
          x: xPos,
          y: yPos,
          group // Atribui o grupo ao nó
        })

        if (parentId !== null) {
          // Adicionar a variável fixada como label da aresta
          edges.push({
            from: parentId,
            to: id,
            label: fixed_variable || '' // Exibe a variável fixada se disponível
          })
        }

        // Se houver filhos, processar nós filhos
        if (branch.branches && branch.branches.length > 0) {
          let currentXPos = xPosition // Centralizar filhos em relação ao pai

          branch.branches.forEach((subBranch, index) => {
            // Deslocamento: à esquerda ou direita do nó pai
            const subXPos = currentXPos + (index === 0 ? -displacement : displacement)
            parseBranch(subBranch, id, depth + 1, subXPos)
          })
        }
      }

      // Iniciar a partir do nó raiz
      parseBranch(tree, null, 0, 0)

      // Marcar o OPT como verde e remover SUP ou INF
      if (optNode) {
        nodes.forEach((node) => {
          if (node.id === optNode.id) {
            node.group = 'maxSolutionNode' // Mudar o grupo para "maxSolutionNode" que será verde
            node.label = node.label.replace(/\[SUP\]|\[INF\]/g, '') // Remover SUP ou INF
            node.label += '[OPT]' // Adicionar o rótulo "OPT" no nó
          }
        })
      }

      // Função para verificar e ajustar sobreposição
      this.adjustNodePositions(nodes, xSpacing)

      return { nodes, edges }
    },
    // Função para verificar e ajustar sobreposição de nós no eixo X
    adjustNodePositions(nodes, minSpacing) {
      // Ordenar nós por sua profundidade (y) para comparar nós em cada nível da árvore
      const nodesByDepth = nodes.reduce((acc, node) => {
        const depth = node.y
        if (!acc[depth]) acc[depth] = []
        acc[depth].push(node)
        return acc
      }, {})

      // Para cada nível (y), verificar se há sobreposição no eixo X
      Object.keys(nodesByDepth).forEach((depth) => {
        const nodesAtDepth = nodesByDepth[depth]

        // Ordenar os nós pelo eixo X
        nodesAtDepth.sort((a, b) => a.x - b.x)

        // Verificar se há sobreposição e ajustar
        for (let i = 1; i < nodesAtDepth.length; i++) {
          const previousNode = nodesAtDepth[i - 1]
          const currentNode = nodesAtDepth[i]

          // Se os nós estiverem muito próximos no eixo X, ajustar o nó atual
          if (currentNode.x - previousNode.x < minSpacing) {
            const overlap = minSpacing - (currentNode.x - previousNode.x)
            currentNode.x += overlap // Ajustar o nó atual para a direita
            previousNode.x -= overlap
          }
        }
      })
    },
    // Função para contar o número de nós no JSON
    countNodesInJson(tree) {
      let count = 0

      const traverseTree = (branch) => {
        count++
        if (branch.branches && branch.branches.length > 0) {
          branch.branches.forEach(traverseTree)
        }
      }

      traverseTree(tree)
      return count
    }
  }
}
</script>
