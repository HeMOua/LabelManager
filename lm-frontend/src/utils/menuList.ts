import { ref } from "vue";
import type { MenuItem } from "@/types/index";

export const menuList =  ref<MenuItem[]>([
  {
    id: '1',
    title: '首页',
    icon: 'House',
    path: '/dashboard'
  },
  {
    id: '2',
    title: '项目管理',
    icon: 'Folder',
    path: '/projects'
  },
  {
    id: '3',
    title: '图库管理',
    icon: 'Picture',
    path: '/gallery'
  },
  {
    id: '4',
    title: '树形浏览',
    icon: 'Operation',
    path: '/tree'
  },
  {
    id: '5',
    title: '标签管理',
    icon: 'CollectionTag',
    path: '/tags'
  }
]);
