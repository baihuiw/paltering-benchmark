# ============================================================================
# make_figures_violin_26.R
# Seaborn-"whitegrid" style violin plots of UNETHICAL by cell (26 scenarios,
# 3 frontier models): full rating distribution per cell + slim inner box with
# white median (violinplot-style) + the 3 per-model means as small points.
#   fig2v_unethical_violin_cold_26 / _informed_26 / _botharms_26
# PNG + PDF to results/figures_combined_26/.
# ============================================================================

suppressPackageStartupMessages({ library(ggplot2); library(dplyr) })

OUT <- "results/figures_combined_26"
d <- read.csv(file.path(OUT, "combined_26_long.csv"), stringsAsFactors = FALSE)

cell_levels <- c("fully_true", "palter", "truthy_falsehood", "blatant_falsehood")
cell_labs <- c(fully_true = "Whole truth\n(V+ G+)", palter = "Palter\n(V+ G-)",
               truthy_falsehood = "Truthy falsehood\n(V- G+)",
               blatant_falsehood = "Blatant falsehood\n(V- G-)")
# seaborn Set3-like pastels
cell_fills <- c(fully_true = "#b3de69", palter = "#fdb462",
                truthy_falsehood = "#80b1d3", blatant_falsehood = "#fb8072")
model_labs <- c(gemini35flash = "Gemini 3.5 Flash", gpt56sol = "GPT-5.6-sol", opus48 = "Opus 4.8")
model_cols <- c(`Gemini 3.5 Flash` = "#66c2a5", `GPT-5.6-sol` = "#fc8d62", `Opus 4.8` = "#8da0cb")

d$cell_type <- factor(d$cell_type, levels = cell_levels)
d$arm_lab <- ifelse(d$arm == "cold", "cold (not informed)", "informed (ground truth given)")
d$mlab <- model_labs[d$model]

theme_sns <- theme_minimal(base_size = 13) +
  theme(panel.grid.major.y = element_line(color = "grey85", linewidth = 0.4),
        panel.grid.major.x = element_blank(),
        panel.grid.minor = element_blank(),
        axis.ticks = element_blank(),
        plot.title = element_text(face = "bold"),
        legend.position = "top")

save2 <- function(p, name, w, h) {
  ggsave(file.path(OUT, paste0(name, ".png")), p, width = w, height = h, dpi = 150)
  ggsave(file.path(OUT, paste0(name, ".pdf")), p, width = w, height = h)
}

violin_panel <- function(dd, title) {
  mm <- dd %>% group_by(cell_type, mlab) %>% summarise(m = mean(unethical), .groups = "drop")
  ggplot(dd, aes(cell_type, unethical)) +
    geom_violin(aes(fill = cell_type), bw = 0.45, trim = TRUE, scale = "width",
                linewidth = 0.5, color = "grey35", alpha = 0.95, show.legend = FALSE) +
    geom_boxplot(width = 0.06, fill = "grey30", color = "grey30",
                 outlier.shape = NA, coef = 0, show.legend = FALSE) +
    stat_summary(fun = median, geom = "point", color = "white", size = 1.8) +
    geom_point(data = mm, aes(cell_type, m, color = mlab),
               position = position_dodge(width = 0.35), size = 2.6, stroke = 0,
               alpha = 0.95) +
    scale_fill_manual(values = cell_fills) +
    scale_color_manual(values = model_cols) +
    scale_x_discrete(labels = cell_labs) +
    scale_y_continuous(limits = c(0.6, 7.4), breaks = 1:7) +
    labs(title = title,
         subtitle = "violin = full rating distribution (all samples); grey box = IQR, white dot = median; colored dots = model means",
         x = NULL, y = "UNETHICAL (1 = not at all, 7 = extremely)", color = NULL) +
    guides(color = guide_legend(override.aes = list(size = 3))) +
    theme_sns
}

for (a in unique(d$arm)) {
  dd <- d[d$arm == a, ]
  p <- violin_panel(dd, sprintf("How unethical is it to post this? (%s, 26 scenarios)", dd$arm_lab[1]))
  save2(p, sprintf("fig2v_unethical_violin_%s_26", a), 9.5, 6)
}

# combined: facet cold | informed for the direct contrast
mmb <- d %>% group_by(arm_lab, cell_type, mlab) %>% summarise(m = mean(unethical), .groups = "drop")
pb <- ggplot(d, aes(cell_type, unethical)) +
  geom_violin(aes(fill = cell_type), bw = 0.45, trim = TRUE, scale = "width",
              linewidth = 0.5, color = "grey35", alpha = 0.95, show.legend = FALSE) +
  geom_boxplot(width = 0.06, fill = "grey30", color = "grey30",
               outlier.shape = NA, coef = 0, show.legend = FALSE) +
  stat_summary(fun = median, geom = "point", color = "white", size = 1.6) +
  geom_point(data = mmb, aes(cell_type, m, color = mlab),
             position = position_dodge(width = 0.35), size = 2.3, stroke = 0, alpha = 0.95) +
  facet_wrap(~arm_lab) +
  scale_fill_manual(values = cell_fills) +
  scale_color_manual(values = model_cols) +
  scale_x_discrete(labels = cell_labs) +
  scale_y_continuous(limits = c(0.6, 7.4), breaks = 1:7) +
  labs(title = "How unethical is it to post this? Cold vs informed (26 scenarios)",
       subtitle = "violin = full rating distribution; grey box = IQR, white dot = median; colored dots = model means",
       x = NULL, y = "UNETHICAL (1-7)", color = NULL) +
  guides(color = guide_legend(override.aes = list(size = 3))) +
  theme_sns + theme(axis.text.x = element_text(size = 9))
save2(pb, "fig2v_unethical_violin_botharms_26", 13.5, 6)

cat("wrote violin figures to", OUT, "\n")
