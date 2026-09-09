# ============================================================================
# make_figures_combined_26.R
# Point plot + perception map for the INFORMED arm, all 26 scenarios
# (s1-18 hand-made + s19-26 disinfo/hostile), 3 frontier models.
#   fig2 - UNETHICAL by cell x model: raw jitter + mean +/- 95% CI
#   fig3 - Perception map: perceived VERBATIM (x) vs GIST (y), per-scenario cell means
# Markers/call-outs left off. PNG + PDF to results/figures_combined_26/.
# ============================================================================

suppressPackageStartupMessages({ library(ggplot2); library(dplyr) })

OUT <- "results/figures_combined_26"
ALL <- read.csv(file.path(OUT, "combined_26_long.csv"), stringsAsFactors = FALSE)

for (ARM in c("cold", "informed")) {
d <- ALL[ALL$arm == ARM, ]

cell_levels <- c("fully_true", "palter", "truthy_falsehood", "blatant_falsehood")
cell_labs <- c(fully_true = "Whole truth\n(V+ G+)", palter = "Palter\n(V+ G-)",
               truthy_falsehood = "Truthy falsehood\n(V- G+)",
               blatant_falsehood = "Blatant falsehood\n(V- G-)")
cell_cols <- c(fully_true = "#2ca02c", palter = "#ff7f0e",
               truthy_falsehood = "#1f77b4", blatant_falsehood = "#d62728")
model_labs <- c(gemini35flash = "Gemini 3.5 Flash", gpt56sol = "GPT-5.6-sol", opus48 = "Opus 4.8")
d$cell_type <- factor(d$cell_type, levels = cell_levels)
d$model     <- factor(d$model, levels = names(model_labs))

base <- theme_minimal(base_size = 12) +
  theme(panel.grid.minor = element_blank(), plot.title = element_text(face = "bold"))
save2 <- function(p, name, w, h) {
  ggsave(file.path(OUT, paste0(name, ".png")), p, width = w, height = h, dpi = 150)
  ggsave(file.path(OUT, paste0(name, ".pdf")), p, width = w, height = h)
}
arm_lab <- if (ARM == "cold") "cold / not-informed" else "informed, ground truth given"
subtitle <- sprintf("%s, 26 scenarios, 3 frontier models (n=%d rows)", arm_lab, nrow(d))

## FIG 2 - point plot: raw jitter + mean +/- 95% CI, per cell x model
s2 <- d %>% group_by(cell_type, model) %>%
  summarise(m = mean(unethical), se = sd(unethical) / sqrt(n()), .groups = "drop") %>%
  mutate(lo = m - 1.96 * se, hi = m + 1.96 * se)
p2 <- ggplot() +
  geom_jitter(data = d, aes(cell_type, unethical, color = model),
              position = position_jitterdodge(jitter.width = 0.16, dodge.width = 0.72),
              alpha = 0.28, size = 1.5) +
  geom_hline(yintercept = 4, linetype = "dotted") +
  geom_errorbar(data = s2, aes(cell_type, ymin = lo, ymax = hi, color = model),
                position = position_dodge(0.7), width = 0.25, linewidth = 0.6) +
  geom_point(data = s2, aes(cell_type, m, color = model),
             position = position_dodge(0.7), size = 2.6) +
  scale_x_discrete(labels = cell_labs) +
  scale_color_brewer(palette = "Set2", labels = model_labs) +
  scale_y_continuous(limits = c(1, 7), breaks = 1:7) +
  labs(title = sprintf("UNETHICAL by cell and model (%s, 26 scenarios)", ARM),
       subtitle = subtitle, x = NULL,
       y = "UNETHICAL (1 = not at all, 7 = extremely)", color = NULL) +
  base + theme(legend.position = "top", panel.grid = element_blank(),
               axis.line = element_line(color = "grey70"))
save2(p2, sprintf("fig2_unethical_pointplot_%s_26", ARM), 9.5, 5.8)

## FIG 3 - perception map: VERBATIM (x) vs GIST (y), per-scenario cell means
s3 <- d %>% group_by(scenario_id, cell_type) %>%
  summarise(V = mean(verbatim), G = mean(gist), .groups = "drop")
ideal <- data.frame(cell_type = factor(cell_levels, levels = cell_levels),
                    V = c(7, 7, 1, 1), G = c(7, 1, 7, 1))
p3 <- ggplot(s3, aes(V, G, color = cell_type)) +
  geom_hline(yintercept = 4, color = "grey75") + geom_vline(xintercept = 4, color = "grey75") +
  geom_point(data = ideal, aes(V, G, color = cell_type), shape = 5, size = 7, stroke = 1.3) +
  geom_point(size = 2.2, alpha = 0.75) +
  annotate("text", x = 6.6, y = 6.9, label = "whole truth", size = 3, color = "grey40", fontface = "italic") +
  annotate("text", x = 6.7, y = 1.1, label = "paltering", size = 3, color = "grey40", fontface = "italic") +
  scale_color_manual(values = cell_cols, labels = cell_labs) +
  scale_x_continuous(limits = c(1, 7), breaks = 1:7) +
  scale_y_continuous(limits = c(1, 7), breaks = 1:7) +
  labs(title = sprintf("Perception map (%s, 26 scenarios)", ARM),
       subtitle = "each point = one scenario's cell mean (3 models pooled); diamonds = ideal position",
       x = "Perceived VERBATIM accuracy (1-7)", y = "Perceived GIST accuracy (1-7)", color = NULL) +
  base + theme(legend.position = "right")
save2(p3, sprintf("fig3_perception_map_%s_26", ARM), 8.5, 6)

cat("wrote fig2 + fig3 (", ARM, ", 26 scenarios)\n")
}  # end arm loop
