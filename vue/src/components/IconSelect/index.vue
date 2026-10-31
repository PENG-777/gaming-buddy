<template>
  <!--
    外层容器，固定高度200像素。
    为什么要固定高度？因为这个选择器通常会作为弹窗或下拉框的内容区域，
    固定高度可以防止它无限扩张，同时内容超出时会自动出现滚动条。
  -->
  <div style="height: 200px;">
    <!--
      Flex布局容器：
      display: flex -> 启用弹性布局，子元素会排成一行
      flex-wrap: wrap -> 允许子元素换行，当一行放不下时会自动换到下一行
      这个容器将负责排列所有的图标项目
    -->
    <div style="display: flex; flex-wrap: wrap;">
      <!--
        v-for循环：遍历iconList数组，为每个图标创建一个div
        item: 当前遍历的图标名称（如"home"、"user"）
        index: 当前图标在数组中的索引位置（0, 1, 2...）

        :key="index":
        - Vue要求在使用v-for时必须给每个项一个唯一的key
        - 这里使用index作为key，因为图标名称不会重复且顺序固定
        - 最佳实践：如果有唯一ID应该用ID，这里没有所以用index

        class="icon-item-wrapper": 应用CSS类名
        @click="selectedIcon(item)": 点击事件绑定
          - 当用户点击这个图标时，调用selectedIcon函数
          - 并把当前图标名称作为参数传递
      -->
      <div
          v-for="(item, index) in iconList"
          class="icon-item-wrapper"
          :key="index"
          @click="selectedIcon(item)"
      >
        <!--
          图标内容容器：
          这个div包含图标本身和图标名称文字
        -->
        <div class="icon-item">
          <!--
            svg-icon组件：
            这是一个自定义的SVG图标组件（通常来自第三方库或自定义组件）

            :icon-class="item":
            - 动态绑定属性，将当前图标名称传给svg-icon组件
            - svg-icon组件会根据这个名称找到对应的SVG文件并显示

            style="height: 25px; width: 16px;":
            - 固定图标尺寸：高25px，宽16px
            - 保持所有图标大小一致，看起来整齐
          -->
          <svg-icon :icon-class="item" style="height: 25px; width: 16px;"/>

          <!--
            显示图标名称：
            {{ item }} 是Vue的文本插值，将图标名称显示为文字
            例如：如果item是"home"，这里就会显示"home"

            为什么显示名称？
            1. 让用户知道这个图标叫什么
            2. 方便搜索或识别
            3. 当图标意思不明确时，文字可以提供说明
          -->
          <span>{{ item }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

// 动态导入所有SVG图标
/*
  问题：我们有很多SVG图标文件，怎么自动获取所有图标？
  解决：使用Vite的import.meta.glob功能

  什么是import.meta.glob？
  - 这是Vite构建工具提供的功能（Webpack也有类似功能）
  - 它可以批量导入匹配特定模式的文件
  - 返回一个对象，键是文件路径，值是一个异步导入函数

  示例：
  假设icons文件夹下有: home.svg, user.svg, settings.svg
  那么modules对象会是：
  {
    '@/assets/icons/svg/home.svg': () => import('@/assets/icons/svg/home.svg'),
    '@/assets/icons/svg/user.svg': () => import('@/assets/icons/svg/user.svg'),
    '@/assets/icons/svg/settings.svg': () => import('@/assets/icons/svg/settings.svg')
  }
*/
const modules = import.meta.glob('@/assets/icons/svg/*.svg');

// 处理图标路径，提取纯名称
/*
  问题：modules对象包含的是完整路径，我们只需要图标名称
  解决：通过字符串处理提取名称

  步骤拆解：
  1. Object.keys(modules) -> 获取所有文件路径的数组
    例如：['@/assets/icons/svg/home.svg', '@/assets/icons/svg/user.svg']

  2. .map(path => ...) -> 对每个路径进行处理

  3. path.split('assets/icons/svg/')[1]
    例如：'@/assets/icons/svg/home.svg'.split('assets/icons/svg/')
    结果：['@/', 'home.svg']
    取[1]：'home.svg'

  4. .split('.svg')[0]
    例如：'home.svg'.split('.svg')
    结果：['home', '']
    取[0]：'home'

  最终icons是一个字符串数组：['home', 'user', 'settings', ...]
*/
const icons = Object.keys(modules).map(path =>
    path.split('assets/icons/svg/')[1].split('.svg')[0]
);

// 图标列表
const iconList = ref(icons);

/*
  定义这个组件可以触发什么事件
  这里定义了一个'selected'事件
  子组件如何通知父组件？
  通过emit函数：emit('事件名', 参数)
  父组件如何监听？
  <icon-selector @selected="handleSelected" />
*/
const emit = defineEmits(['selected']);

/*
  图标点击处理函数
  当用户点击图标时执行这个函数

  参数name：被点击的图标名称

  函数做的事情：
  1. 触发'selected'事件，把图标名称传给父组件
     父组件就可以知道用户选择了哪个图标

  2. document.body.click()
     这是一个特殊技巧：模拟点击页面body
     为什么需要这个？
     这个图标选择器是一个下拉框或弹窗：
     - 用户点击图标后，通常希望下拉框自动关闭
     - 通过触发body的点击事件，可以让监听body点击的关闭逻辑执行
     - 这是一种常见的方式让其他组件知道"用户在外面点击了"
*/
const selectedIcon = (name) => {
  // 通知父组件：用户选择了哪个图标
  emit('selected', name);

  // 模拟点击body，通常用于触发关闭下拉框的逻辑
  document.body.click();
};
</script>

<style scoped>
/* 每个图标容器：占1/3宽度，固定高度 */
.icon-item-wrapper {
  width: calc(100% / 3);  /* 一行显示3个图标 */
  height: 25px;           /* 固定高度 */
  line-height: 25px;      /* 文字垂直居中 */
  cursor: pointer;        /* 鼠标指针变为手型 */
  display: flex;          /* 内部使用flex布局 */
}

/* 图标内容区域 */
.icon-item {
  display: flex;          /* 图标和文字水平排列 */
  max-width: 100%;        /* 防止内容溢出 */
  height: 100%;           /* 继承父容器高度 */
  padding: 0 5px;         /* 左右内边距 */
}

/* 鼠标悬停效果 */
.icon-item:hover {
  background: #ececec;    /* 浅灰色背景 */
}
</style>
