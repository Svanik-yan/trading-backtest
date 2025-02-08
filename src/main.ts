import { createApp } from '@vue/runtime-dom'
import App from './App.vue'
import { createPinia } from 'pinia'

// 导入 Vant 核心组件和样式
import { 
  Button, 
  NavBar, 
  Field, 
  CellGroup,
  Cell,
  Popup, 
  Calendar,
  List,
  Tag,
  Icon,
  Empty,
  Tab,
  Tabs,
  Search,
  Loading,
  DatePicker
} from 'vant'
import 'vant/lib/index.css'

// 创建应用
const app = createApp(App)

// 安装 Pinia
app.use(createPinia())

// 安装核心组件
app.use(Button)
app.use(NavBar)
app.use(Field)
app.use(CellGroup)
app.use(Cell)
app.use(Popup)
app.use(Calendar)
app.use(List)
app.use(Tag)
app.use(Icon)
app.use(Empty)
app.use(Tab)
app.use(Tabs)
app.use(Search)
app.use(Loading)
app.use(DatePicker)

// 挂载应用
app.mount('#app')

// 调试用
console.log('App mounted') 