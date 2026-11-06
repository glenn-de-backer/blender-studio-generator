# Simple Studio Generator for Blender

A Blender extension and add-on designed to quickly generate parametric cycloramas, studio backdrops, and coordinated lighting rigs for product renders, character showcases, and scene staging.

---

## ✨ Features

- **Parametric Studio Backdrops**: Generate curved infinity coves, corner cycloramas, and ceiling stages with non-destructive dimension and bevel adjustments.
- **Automated Lighting Rigs**: Set up synchronized Softbox, Three-Point, or Overhead lighting rigs scaled automatically to the studio dimensions.
- **Granular Light Controls**: Customize master power, horizontal spread, and overall tint, or fine-tune individual lamps with dedicated power, color, and positioning controls.
- **Blender 4.2+ Compatible**: Built natively for Blender's Extensions platform as well as standard disk installation.

---

## 📥 Installation

1. Download or locate `studio_generator_1.0.0.zip`.
2. Open Blender and navigate to **Edit** > **Preferences**.
3. Select **Get Extensions** (or **Add-ons**).
4. Click the top-right menu dropdown (arrow icon) and choose **Install from Disk...**.
5. Select `studio_generator_1.0.0.zip`.
6. Ensure the extension is enabled in the list.

---

## 🚀 How to Use

### 1. Add a Studio Backdrop
- In the **3D Viewport**, press <kbd>N</kbd> to open the Sidebar and select the **Studio** tab (or use **Add** > **Mesh** > **Studio Backdrop**).
- Click **Add Studio** and pick an initial preset shape.

### 2. Configure Geometry
- Adjust the dimensions (**Width**, **Depth**, **Wall Height**) and curve bevels (**Floor Curve Radius**, **Segments**) live in the panel.
- Tweak the quick material settings (**Base Color**, **Roughness**) directly from the sidebar.

### 3. Add & Customize Lighting
- Under **Optional Lighting**, select a rig setup (e.g., *Three Point*, *Softbox Pair*, or *Overhead*).
- Use **Horizontal Spread** to widen or narrow the rig's placement around your subject.
- Expand individual lamp drawers (Key, Fill, Rim, Top) to adjust per-lamp wattage, toggle lights on/off, or switch the rim light position.

### 4. Finalize
- Use **Rebuild Studio** if you need to refresh geometry.
- Click **Bake Studio** when you are ready to convert the parametric studio into a standard, static mesh.

---

## ⚙️ Parameter & Option Reference

### 📐 Geometry & Backdrop

| Option | Values / Range | Description |
| :--- | :--- | :--- |
| **Shape (`preset`)** | `L`, `U`, `CORNER`, `C`, `S`, `FLAT` | The primary cyclorama curve profile: <br>• **L**: Standard floor-to-wall single curve.<br>• **U**: Three-sided curved cove.<br>• **CORNER**: 90° corner wall cove.<br>• **C**: Floor, wall, and curved ceiling return.<br>• **S**: Floor cove with downward front drop.<br>• **FLAT**: Flat seamless floor stage. |
| **Corner Side** | `Left`, `Right` | *(CORNER preset only)* Determines which side the adjoining corner wall extends from. |
| **Width / Depth / Wall Height** | Distance (meters) | Overall bounds and footprint of the studio backdrop. |
| **Floor Curve Radius** | Distance (meters) | Radius of the smooth transition between floor and wall. Automatically clamped if dimensions are too small to prevent overlapping geometry. |
| **Second Curve Radius** | Distance (meters) | *(C and S presets only)* Curvature radius for the ceiling return or front drop curve. |
| **Ceiling Reach / Front Drop** | Distance (meters) | Forward extent of the ceiling canopy (`C`) or vertical drop depth (`S`). |
| **Curve Segments** | 3 – 128 (Default: 24) | Polygon density across the bevel curves. Higher values produce smoother reflections under direct lighting. |
| **Thickness** | Distance (meters) | Solidify thickness applied to the backdrop shell. Set to `0.0` for a single-sided surface. |

---

### 💡 Lighting Rigs

| Rig Setup | Included Lamps | Best Used For |
| :--- | :--- | :--- |
| **None** | *None* | Removes all generated studio lights and leaves existing scene lights untouched. |
| **Softbox Pair** | Key, Fill | Clean, broad illumination suited for soft product photography and e-commerce shots. |
| **Three Point** | Key, Fill, Rim | Classic portrait and showcase lighting with subject-background silhouette separation. |
| **Overhead** | Top, Front Fill | Top-down diffuse softbox combined with subtle forward fill; ideal for automotive, tech, and tabletop renders. |

---

### 🎛️ Master Lighting Controls

- **Softbox Size**: Sets the base area-light disk diameter, proportionally scaled across each lamp role.
- **Horizontal Spread**: Controls how far the lights sit from the studio center (0.2x to 1.1x scaling).
- **Overall Tint**: Global RGB color multiplier applied to all active lamps simultaneously.

---

### 🔦 Individual Light Controls

Each active light in the chosen preset has an expandable drawer with granular overrides:

- **Enable Toggle**: Quickly mute or enable individual lights without removing them from the rig.
- **Power (W)**: Direct wattage control for each individual light (Key, Fill, Rim, Top, Front Fill).
- **Color**: Individual lamp tint combined with the master color tint.
- **Rim Position** *(Three-Point Setup)*:
  - **Back Left**: Cross-angles the rim light opposite standard key setups, preventing highlight blowouts.
  - **Back Center**: Directly behind the subject for a symmetrical halo/rim on both edges.
  - **Back Right**: Positions the rim light behind and to the right of the subject.

---

## 💡 Quick Tips

- **Real-World Scale**: Apply the scale (<kbd>Ctrl</kbd> + <kbd>A</kbd> > **Apply Scale**) of your subject models before sizing the studio to ensure accurate physical light falloff.
- **Auto-Aiming**: Managed lamps dynamically parent to the studio object and aim at the studio center focus point automatically. Moving or rotating the studio backdrop moves the entire lighting setup with it.
- **Baking Geometry**: If you want to manually edit vertices, apply modifiers, or export the cyclorama to FBX/glTF, click **Bake Studio** to finalize the object into standard Blender geometry.