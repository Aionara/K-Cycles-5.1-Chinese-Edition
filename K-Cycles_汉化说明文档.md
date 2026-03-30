# K-Cycles 5.1 汉化说明文档

## 📋 汉化概述

**汉化作者**: B站UP主-记忆面包拯救我
**文档版本**: 1.1  
**最后更新**: 2026-03-30  
**适用版本**: K-Cycles 2026 5.1  

本文档详细记录了 K-Cycles 2026 5.1 版本的汉化工作内容，包括所有已翻译的文件和具体翻译内容。

---

## 🗂️ 汉化文件清单

### 1. properties.py（主要属性文件）
**文件路径**: `scripts/addons_core/cycles/properties.py`

#### 已汉化内容：
- **K-Cycles 模式**
  - `K-Cycles Mode` → `K-Cycles 模式`
  - 描述: "Select K-Cycles mode" → "选择 K-Cycles 模式"

- **GPU 加速**
  - `GPU Acceleration` → `GPU 加速`
  - 描述: "Enable GPU acceleration" → "启用 GPU 加速"

- **全局光照预设**
  - `Global Illumination Preset` → `全局光照预设`
  - 描述: "Select global illumination preset" → "选择全局光照预设"

- **采样设置**
  - `Samples` → `采样数`
  - `Viewport Samples` → `视口采样数`
  - `Render Samples` → `渲染采样数`

- **降噪设置**
  - `Denoising` → `降噪`
  - `Viewport Denoising` → `视口降噪`
  - `Render Denoising` → `渲染降噪`

---

### 2. kcycles_playback.py（播放模式）
**文件路径**: `scripts/addons_core/cycles/kcycles_playback.py`

#### 已汉化内容：
- **播放模式**
  - `Playback Mode` → `播放模式`
  - 描述: "Select playback mode" → "选择播放模式"

- **时序稳定**
  - `Temporal Stability` → `时序稳定`
  - 描述: "Enable temporal stability" → "启用时序稳定"

- **帧插值**
  - `Frame Interpolation` → `帧插值`
  - 描述: "Enable frame interpolation" → "启用帧插值"

- **自适应采样**
  - `Adaptive Sampling` → `自适应采样`
  - 描述: "Enable adaptive sampling" → "启用自适应采样`

---

### 3. kcycles_postfx.py（后期特效）
**文件路径**: `scripts/addons_core/cycles/kcycles_postfx.py`

#### 已汉化内容：
- **辉光 (Bloom)**
  - `Bloom` → `辉光`
  - `Bloom Intensity` → `辉光强度`
  - `Bloom Radius` → `辉光半径`
  - `Bloom Threshold` → `辉光阈值`

- **光晕 (Glare)**
  - `Glare` → `光晕`
  - `Glare Type` → `光晕类型`
  - `Glare Intensity` → `光晕强度`

- **镜头效果 (Lens)**
  - `Lens` → `镜头`
  - `Lens Distortion` → `镜头畸变`
  - `Lens Chromatic Aberration` → `镜头色差`
  - `Lens Vignette` → `镜头暗角`

- **色调映射 (Tone Mapping)**
  - `Tone Mapping` → `色调映射`
  - `Tone Mapping Type` → `色调映射类型`
  - `Exposure` → `曝光`
  - `Gamma` → `伽马`
  - `Filmic` → `电影化`
  - `Standard` → `标准`

---

### 4. kcycles_lightgroups.py（灯光组）
**文件路径**: `scripts/addons_core/cycles/kcycles_lightgroups.py`

#### 已汉化内容：
- **灯光组**
  - `Light Groups` → `灯光组`
  - `Add Light Group` → `添加灯光组`
  - `Remove Light Group` → `移除灯光组`
  - `Light Group Name` → `灯光组名称`

- **灯光强度**
  - `Light Intensity` → `灯光强度`
  - `Light Color` → `灯光颜色`

---

### 5. kcycles_render_cameras.py（渲染相机）
**文件路径**: `scripts/addons_core/cycles/kcycles_render_cameras.py`

#### 已汉化内容：
- **渲染相机**
  - `Render Cameras` → `渲染相机`
  - `Add Render Camera` → `添加渲染相机`
  - `Remove Render Camera` → `移除渲染相机`
  - `Camera Settings` → `相机设置`

---

### 6. operators.py（操作符）
**文件路径**: `scripts/addons_core/cycles/operators.py`

#### 已汉化内容：
- **使用节点操作符**
  - 类名: `CYCLES_OT_use_shading_nodes`
  - 描述: `"Enable nodes on a light"` → `"在灯光上启用节点"`
  - 标签: `"Use Nodes"` → `"使用节点"`

- **动画降噪操作符**
  - 类名: `CYCLES_OT_denoise_animation`
  - 描述: `"Denoise rendered animation sequence..."` → `"使用当前场景和视图层设置对渲染的动画序列进行降噪。需要降噪数据通道并输出到 OpenEXR 多层文件"`
  - 标签: `"Denoise Animation"` → `"动画降噪"`
  - 属性:
    - `Input Filepath` → `输入文件路径`
    - `Output Filepath` → `输出文件路径`
  - 错误信息: `"Frame '%s' not found, animation must be complete"` → `"未找到帧 '%s'，动画必须完整"`
  - 完成信息: `"Denoising completed"` → `"降噪完成"`

- **合并图像操作符**
  - 类名: `CYCLES_OT_merge_images`
  - 描述: `"Combine OpenEXR multi-layer images..."` → `"将使用不同采样范围渲染的 OpenEXR 多层图像合并为一张噪点更少的图像"`
  - 标签: `"Merge Images"` → `"合并图像"`
  - 属性:
    - `Input Filepath` → `输入文件路径`
    - `Output Filepath` → `输出文件路径`

---

### 7. presets.py（预设）
**文件路径**: `scripts/addons_core/cycles/presets.py`

#### 已汉化内容：
- **积分器预设**
  - 类名: `AddPresetIntegrator`
  - 文档: `"Add an Integrator Preset"` → `"添加积分器预设"`
  - 标签: `"Add Integrator Preset"` → `"添加积分器预设"`

- **采样预设**
  - 类名: `AddPresetSampling`
  - 文档: `"Add a Sampling Preset"` → `"添加采样预设"`
  - 标签: `"Add Sampling Preset"` → `"添加采样预设"`

- **视口采样预设**
  - 类名: `AddPresetViewportSampling`
  - 文档: `"Add a Viewport Sampling Preset"` → `"添加视口采样预设"`
  - 标签: `"Add Viewport Sampling Preset"` → `"添加视口采样预设"`

- **性能预设**
  - 类名: `AddPresetPerformance`
  - 文档: `"Add an Performance Preset"` → `"添加性能预设"`
  - 标签: `"Add Performance Preset"` → `"添加性能预设"`

- **K-Cycles 后期特效预设**
  - 类名: `AddPresetKCyclesPostFX`
  - 文档: `"Add a K-Cycles Post FX Preset"` → `"添加 K-Cycles 后期特效预设"`
  - 标签: `"Add K-Cycles Post FX Preset"` → `"添加 K-Cycles 后期特效预设"`

- **K-Cycles 辉光预设**
  - 类名: `AddPresetKCyclesBloom`
  - 文档: `"Add a K-Cycles Bloom Preset"` → `"添加 K-Cycles 辉光预设"`
  - 标签: `"Add K-Cycles Bloom Preset"` → `"添加 K-Cycles 辉光预设"`

- **K-Cycles 色调映射预设**
  - 类名: `AddPresetKCyclesTonemapping`
  - 文档: `"Add a K-Cycles Tone Mapping Preset"` → `"添加 K-Cycles 色调映射预设"`
  - 标签: `"Add K-Cycles Tone Mapping Preset"` → `"添加 K-Cycles 色调映射预设"`

- **K-Cycles 镜头预设**
  - 类名: `AddPresetKCyclesLens`
  - 文档: `"Add a K-Cycles Lens Preset"` → `"添加 K-Cycles 镜头预设"`
  - 标签: `"Add K-Cycles Lens Preset"` → `"添加 K-Cycles 镜头预设"`

- **K-Cycles 灯光组预设**
  - 类名: `AddPresetKCyclesLightgroups`
  - 文档: `"Add a K-Cycles Lightgroups Preset"` → `"添加 K-Cycles 灯光组预设"`
  - 标签: `"Add K-Cycles Lightgroups Preset"` → `"添加 K-Cycles 灯光组预设"`

---

## 🚀 K-Cycles 5.1 功能说明

### 一、核心特性

#### 1. 极速渲染
K-Cycles 是 Cycles 渲染引擎的高度优化版本，通过以下技术实现更快的渲染速度：
- **GPU 加速优化**：充分利用 NVIDIA/AMD GPU 的计算能力
- **自适应采样**：智能分配采样资源，减少噪点区域
- **时序稳定**：动画渲染时保持帧间一致性

#### 2. 智能降噪
- **视口降噪**：实时预览降噪效果
- **渲染降噪**：最终输出高质量降噪图像
- **动画降噪**：专门优化的动画序列降噪工具

#### 3. 后期特效系统
内置强大的后期处理功能，无需离开 Blender 即可完成：
- **辉光效果**：模拟真实镜头的光晕效果
- **镜头畸变**：添加真实的镜头变形效果
- **色差效果**：模拟镜头色散
- **暗角效果**：增强画面氛围
- **色调映射**：多种专业的色彩映射方案

---

### 二、主要功能模块

#### 1. 渲染设置
```
渲染属性面板 → K-Cycles
```
- **渲染模式**：选择 GPU/CPU 渲染
- **采样设置**：控制渲染质量和速度
- **降噪选项**：开启/关闭降噪功能
- **全局光照预设**：快速选择光照方案

#### 2. 视口设置
```
视图层属性 → K-Cycles 视口
```
- **视口采样**：控制预览质量
- **视口降噪**：实时降噪预览
- **自适应采样**：智能优化预览性能

#### 3. 后期特效
```
渲染属性面板 → K-Cycles Post FX
```
- **辉光**：调整强度、半径、阈值
- **光晕**：选择类型和强度
- **镜头**：畸变、色差、暗角
- **色调映射**：曝光、伽马、类型选择

#### 4. 灯光组
```
渲染属性面板 → K-Cycles Lightgroups
```
- **创建灯光组**：将灯光分组管理
- **独立控制**：单独调整每组灯光强度
- **后期调整**：渲染后仍可修改灯光效果

#### 5. 渲染相机
```
渲染属性面板 → K-Cycles Render Cameras
```
- **多相机渲染**：同时渲染多个相机视角
- **批量输出**：自动保存不同相机的渲染结果

---

### 三、使用技巧

#### 1. 快速开始
1. 在渲染属性面板选择 **K-Cycles** 引擎
2. 启用 **GPU 加速** 以获得最佳性能
3. 根据场景选择合适的 **全局光照预设**
4. 调整采样设置平衡质量和速度

#### 2. 优化渲染速度
- 使用 **自适应采样** 自动优化
- 降低 **视口采样** 提高交互性能
- 启用 **时序稳定** 优化动画渲染

#### 3. 后期处理流程
1. 渲染完成后进入 **Post FX** 面板
2. 启用需要的特效（辉光、镜头等）
3. 调整参数达到理想效果
4. 使用 **色调映射** 调整整体色彩

#### 4. 灯光组使用
1. 在 **Lightgroups** 面板创建新组
2. 将场景灯光分配到不同组
3. 渲染后可单独调整每组强度
4. 支持保存为预设重复使用

---

### 四、注意事项

1. **GPU 兼容性**：确保显卡驱动为最新版本
2. **显存管理**：复杂场景可能需要调整贴图分辨率
3. **降噪设置**：高噪点场景建议增加采样数
4. **预设保存**：常用设置可保存为预设方便复用

---

## 📁 文件修改记录

### 修改的文件列表
1. `scripts/addons_core/cycles/properties.py`
2. `scripts/addons_core/cycles/kcycles_playback.py`
3. `scripts/addons_core/cycles/kcycles_postfx.py`
4. `scripts/addons_core/cycles/kcycles_lightgroups.py`
5. `scripts/addons_core/cycles/kcycles_render_cameras.py`
6. `scripts/addons_core/cycles/operators.py`
7. `scripts/addons_core/cycles/presets.py`

### 未修改的文件
- `camera.py` - 技术代码，无UI文本
- `engine.py` - 技术代码，无UI文本
- `version_update.py` - 版本更新逻辑，无UI文本
- `ui.py` - 已在之前汉化完成

---

## 📝 更新日志

### 2026-03-30
- ✅ 完成 operators.py 汉化
- ✅ 完成 presets.py 汉化
- ✅ 整理汉化说明文档
- ✅ 编写 K-Cycles 5.1 功能说明

### 之前已完成
- ✅ properties.py 汉化
- ✅ kcycles_playback.py 汉化
- ✅ kcycles_postfx.py 汉化
- ✅ kcycles_lightgroups.py 汉化
- ✅ kcycles_render_cameras.py 汉化

---

## 📊 汉化统计

### 翻译数据概览
| 类别 | 数量 |
|------|------|
| 汉化文件数 | 7 个 |
| 汉化类/操作符 | 20+ 个 |
| 汉化属性/参数 | 100+ 个 |
| 汉化预设类型 | 9 种 |

### 汉化覆盖范围
- ✅ 渲染设置面板
- ✅ 视口设置面板
- ✅ 后期特效面板
- ✅ 灯光组面板
- ✅ 渲染相机面板
- ✅ 操作符菜单
- ✅ 预设系统

---

## 🎯 专业术语对照表

### 渲染术语
| 英文 | 中文 | 说明 |
|------|------|------|
| Sampling | 采样 | 控制渲染质量和噪点 |
| Denoising | 降噪 | 去除渲染噪点 |
| Global Illumination | 全局光照 | 间接光照计算 |
| BVH | 层次包围盒 | 场景加速结构 |
| Embree | 英特尔渲染库 | 高性能光线追踪 |

### 后期特效术语
| 英文 | 中文 | 说明 |
|------|------|------|
| Bloom | 辉光 | 高光溢出效果 |
| Glare | 光晕 | 镜头光晕效果 |
| Tone Mapping | 色调映射 | 色彩范围转换 |
| Chromatic Aberration | 色差 | 镜头色散效果 |
| Vignette | 暗角 | 画面边缘变暗 |

### GPU加速术语
| 英文 | 中文 | 说明 |
|------|------|------|
| GPU Boost | GPU加速 | 显卡性能提升 |
| Performance Mode | 性能模式 | 渲染质量/速度平衡 |
| Temporal Stability | 时序稳定 | 动画帧间一致性 |
| Adaptive Sampling | 自适应采样 | 智能采样分配 |

---

## 🔧 技术支持

### 常见问题

**Q: 汉化后界面显示乱码怎么办？**
A: 请确保 Blender 使用 UTF-8 编码，并在偏好设置中将界面语言设置为简体中文。

**Q: 如何恢复英文界面？**
A: 将备份的原始文件覆盖回相应位置即可恢复。

**Q: 汉化是否影响渲染结果？**
A: 不会，汉化仅修改界面文本，不影响渲染算法和输出质量。

**Q: 升级 K-Cycles 后汉化会丢失吗？**
A: 是的，升级后需要重新应用汉化文件。

### 参考资源
- K-Cycles 官方文档: https://www.k-cycles.com
- Blender 官方社区: https://www.blender.org/community/
- Blender 中文社区: https://www.blendercn.org

---

## 📝 更新日志

### v1.1 (2026-03-30)
- ✅ 新增专业术语对照表
- ✅ 新增汉化统计数据
- ✅ 新增常见问题解答
- ✅ 完善功能说明文档

### v1.0 (2026-03-30)
- ✅ 完成 operators.py 汉化
- ✅ 完成 presets.py 汉化
- ✅ 整理汉化说明文档
- ✅ 编写 K-Cycles 5.1 功能说明

### 之前已完成
- ✅ properties.py 汉化
- ✅ kcycles_playback.py 汉化
- ✅ kcycles_postfx.py 汉化
- ✅ kcycles_lightgroups.py 汉化
- ✅ kcycles_render_cameras.py 汉化

---

## ⚖️ 免责声明

本汉化仅供学习和研究使用，请勿用于商业用途。
K-Cycles 是独立软件，其版权归原开发者所有。
汉化文件基于开源协议进行修改，遵循原软件的许可证条款。

---


