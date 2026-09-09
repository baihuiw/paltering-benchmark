# ============================================================================
# make_figures_pilot_s19_26.R
# Figures for the s19-26 pilot (disinfo + hostile-gist), COLD and INFORMED arms.
# Four panel types per arm, in the style of the reference composite:
#   fig1 - Unethicality by cell x model (grouped bars)
#   fig2 - UNETHICAL point plot: raw jitter + mean +/- 95% CI, per cell x model
#   fig3 - Perception map: perceived VERBATIM (x) vs GIST (y), per-scenario cell means
#   fig4 - Palter UNETHICAL by scenario (sorted)
# Hand-drawn markers (arrows / text call-outs / zoom circles) are intentionally
# left off - add them by hand.  Outputs PNG + PDF to results/figures_pilot_s19_26/.
#   Rscript make_figures_pilot_s19_26.R
# ============================================================================

suppressPackageStartupMessages({ library(ggplot2); library(dplyr) })

OUT <- "results/figures_pilot_s19_26"
df  <- read.csv(file.path(OUT, "pilot_s19_26_long.csv"), stringsAsFactors = FALSE)

cell_levels <- c("fully_true", "palter", "truthy_falsehood", "blatant_falsehood")
cell_labs <- c(fully_true = "Whole truth\n(V+ G+)", palter = "Palter\n(V+ G-)",
               truthy_falsehood = "Truthy falsehood\n(V- G+)",
               blatant_falsehood = "Blatant falsehood\n(V- G-)")
cell_cols <- c(fully_true = "#2ca02c", palter = "#ff7f0e",
               truthy_falsehood = "#1f77b4", blatant_falsehood = "#d62728")
model_labs <- c(gemini35flash = "Gemini 3.5 Flash", gpt56sol = "GPT-5.6-sol",
                opus48 = "Opus 4.8", qwen37plus = "Qwen 3.7+",
                deepseekv4pro = "DeepSeek v4-pro")
model_levels <- names(model_labs)
scen_short <- c(s19 = "arms", s20 = "biolabs", s21 = "refugees", s22 = "P&G",
                s23 = "Gates chip", s24 = "Jewell", s25 = "Swift", s26 = "FEMA $750")

df$cell_type <- factor(df$cell_type, levels = cell_levels)
df$model     <- factor(df$model, levels = model_levels)

save2 <- function(p, name, w, h) {
  ggsave(file.path(OUT, paste0(name, ".png")), p, width = w, height = h, dpi = 150)
  ggsave(file.path(OUT, paste0(name, ".pdf")), p, width = w, height = h)
}

base <- theme_minimal(base_size = 12) +
  theme(panel.grid.minor = element_blank(), plot.title = element_text(face = "bold"))

for (a in c("cold", "informed")) {
  d <- df[df$arm == a, ]
  arm_lab <- if (a == "cold") "cold / not-informed" else "informed, ground truth given"

  ## FIG 1 - grouped bars: mean UNETHICAL by cell x model
  s1 <- d %>% group_by(cell_type, model) %>%
    summarise(m = mean(unethical), .groups = "drop")
  p1 <- ggplot(s1, aes(cell_type, m, fill = model)) +
    geom_col(position = position_dodge(0.8), width = 0.75) +
    geom_hline(yintercept = 4, linetype = "dotted") +
    scale_x_discrete(labels = cell_labs) +
    scale_fill_brewer(palette = "Set2", labels = model_labs) +
    scale_y_continuous(limits = c(0, 7), breaks = 1:7, expand = expansion(mult = c(0, 0.02))) +
    labs(title = paste0("Unethicality perceived by models (", arm_lab, ")"),
         x = NULL, y = "Mean UNETHICAL (1 = fine to post, 7 = very unethical)", fill = NULL) +
    base + theme(legend.position = "top")
  save2(p1, paste0("fig1_unethical_by_cell_", a), 9, 5)

  ## FIG 2 - point plot: raw jitter + mean +/- 95% CI, per cell x model
  s2 <- d %>% group_by(cell_type, model) %>%
    summarise(m = mean(unethical), se = sd(unethical) / sqrt(n()), .groups = "drop") %>%
    mutate(lo = m - 1.96 * se, hi = m + 1.96 * se)
  p2 <- ggplot() +
    geom_jitter(data = d, aes(cell_type, unethical, color = model),
                position = position_jitterdodge(jitter.width = 0.18, dodge.width = 0.7),
                alpha = 0.10, size = 0.5) +
    geom_hline(yintercept = 4, linetype = "dotted") +
    geom_errorbar(data = s2, aes(cell_type, ymin = lo, ymax = hi, color = model),
                  position = position_dodge(0.7), width = 0.25, linewidth = 0.6) +
    geom_point(data = s2, aes(cell_type, m, color = model),
               position = position_dodge(0.7), size = 2.4) +
    scale_x_discrete(labels = cell_labs) +
    scale_color_brewer(palette = "Set2", labels = model_labs) +
    scale_y_continuous(limits = c(1, 7), breaks = 1:7) +
    labs(title = paste0("UNETHICAL by cell and model (", arm_lab, ")"),
         x = NULL, y = "UNETHICAL (1 = not at all, 7 = extremely)", color = NULL) +
    base + theme(legend.position = "top")
  save2(p2, paste0("fig2_unethical_pointplot_", a), 9, 5.5)

  ## FIG 3 - perception map: VERBATIM (x) vs GIST (y), per-scenario cell means
  s3 <- d %>% group_by(scenario_id, cell_type) %>%
    summarise(V = mean(verbatim), G = mean(gist), .groups = "drop")
  ideal <- data.frame(cell_type = factor(cell_levels, levels = cell_levels),
                      V = c(7, 7, 1, 1), G = c(7, 1, 7, 1))
  p3 <- ggplot(s3, aes(V, G, color = cell_type)) +
    geom_hline(yintercept = 4, color = "grey75") +
    geom_vline(xintercept = 4, color = "grey75") +
    geom_point(data = ideal, aes(V, G, color = cell_type), shape = 5, size = 7, stroke = 1.3) +
    geom_point(size = 2.4, alpha = 0.85) +
    annotate("text", x = 6.7, y = 6.9, label = "whole truth", size = 3, color = "grey40", fontface = "italic") +
    annotate("text", x = 6.7, y = 1.1, label = "paltering", size = 3, color = "grey40", fontface = "italic") +
    scale_color_manual(values = cell_cols, labels = cell_labs) +
    scale_x_continuous(limits = c(1, 7), breaks = 1:7) +
    scale_y_continuous(limits = c(1, 7), breaks = 1:7) +
    labs(title = paste0("Perception map (", arm_lab, ")"),
         subtitle = "each point = one scenario's cell mean; diamonds = ideal position",
         x = "Perceived VERBATIM accuracy (1-7)",
         y = "Perceived GIST accuracy (1-7)", color = NULL) +
    base + theme(legend.position = "right")
  save2(p3, paste0("fig3_perception_map_", a), 8.5, 6)

  ## FIG 4 - palter UNETHICAL by scenario (sorted)
  s4 <- d %>% filter(cell_type == "palter") %>% group_by(scenario_id) %>%
    summarise(m = mean(unethical), .groups = "drop") %>%
    mutate(lab = scen_short[scenario_id]) %>% arrange(desc(m))
  s4$lab <- factor(s4$lab, levels = s4$lab)
  p4 <- ggplot(s4, aes(lab, m)) +
    geom_col(fill = "#ff7f0e", width = 0.72) +
    geom_text(aes(label = sprintf("%.1f", m)), vjust = -0.4, size = 3.6) +
    geom_hline(yintercept = 4, linetype = "dotted") +
    scale_y_continuous(limits = c(0, 7), breaks = 1:7, expand = expansion(mult = c(0, 0.03))) +
    labs(title = paste0("Which palter got condemned most? (", arm_lab, ")"),
         x = NULL, y = "Palter UNETHICAL (1-7)") +
    base + theme(axis.text.x = element_text(angle = 30, hjust = 1))
  save2(p4, paste0("fig4_palter_by_scenario_", a), 8, 5)
}

cat("wrote", length(list.files(OUT, pattern = "\\.(png|pdf)$")), "figure files to", OUT, "\n")
