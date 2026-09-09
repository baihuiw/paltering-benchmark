# ============================================================================
# make_figures_recognition.R
# Palter-decomposition figures for the s19-26 recognition battery.
#   fig5 - Extraction vs Evaluation per model (grouped bars): shows the gap
#          (R3 evaluation ~100%, R2 extraction 22-65% = extraction is the bottleneck)
#   fig6 - Extraction predicts judgment (scatter): R2 extraction% vs T1-cold
#          palter GIST, one point per model (more extraction -> catches palter)
# Markers/annotations left off. PNG + PDF to results/figures_pilot_s19_26/.
# ============================================================================

suppressPackageStartupMessages({ library(ggplot2); library(dplyr); library(tidyr) })

OUT <- "results/figures_pilot_s19_26"
d   <- read.csv(file.path(OUT, "palter_decomposition.csv"), stringsAsFactors = FALSE)
model_labs <- c(gemini35flash = "Gemini 3.5 Flash", gpt56sol = "GPT-5.6-sol",
                opus48 = "Opus 4.8", qwen37plus = "Qwen 3.7+", deepseekv4pro = "DeepSeek v4-pro")
d$mlab <- model_labs[d$model]
base <- theme_minimal(base_size = 12) +
  theme(panel.grid.minor = element_blank(), plot.title = element_text(face = "bold"))
save2 <- function(p, name, w, h) {
  ggsave(file.path(OUT, paste0(name, ".png")), p, width = w, height = h, dpi = 150)
  ggsave(file.path(OUT, paste0(name, ".pdf")), p, width = w, height = h)
}

## FIG 5 - extraction vs evaluation (grouped bars)
long <- d %>%
  select(mlab, `R2: extracts implicature` = r2_extract, `R3: evaluates gist false` = r3_eval) %>%
  pivot_longer(-mlab, names_to = "probe", values_to = "pct") %>%
  mutate(mlab = factor(mlab, levels = d$mlab[order(d$r2_extract)]))
p5 <- ggplot(long, aes(mlab, pct, fill = probe)) +
  geom_col(position = position_dodge(0.8), width = 0.72) +
  geom_text(aes(label = sprintf("%.0f%%", pct)),
            position = position_dodge(0.8), vjust = -0.4, size = 3.3) +
  scale_fill_manual(values = c("R2: extracts implicature" = "#ff7f0e",
                               "R3: evaluates gist false" = "#1f77b4")) +
  scale_y_continuous(limits = c(0, 108), breaks = seq(0, 100, 25)) +
  labs(title = "Palter-blindness lives in EXTRACTION, not evaluation",
       subtitle = "every model can evaluate the false gist (R3 ~100%); most fail to extract it from the palter (R2)",
       x = NULL, y = "% of palter samples", fill = NULL) +
  base + theme(legend.position = "top", axis.text.x = element_text(angle = 20, hjust = 1))
save2(p5, "fig5_palter_decomposition", 8.5, 5.5)

## FIG 6 - extraction predicts judgment (scatter)
p6 <- ggplot(d, aes(r2_extract, t1_cold_gist)) +
  geom_hline(yintercept = 4, linetype = "dotted", color = "grey60") +
  geom_smooth(method = "lm", se = FALSE, color = "grey70", linewidth = 0.7) +
  geom_point(size = 3, color = "#ff7f0e") +
  geom_text(aes(label = mlab), vjust = -0.9, size = 3.4) +
  scale_x_continuous(limits = c(15, 75)) +
  scale_y_continuous(limits = c(2.5, 5), breaks = seq(2.5, 5, 0.5)) +
  labs(title = "Implicature-extraction predicts palter judgment",
       subtitle = "models that extract the implicature more (R2) rate the palter's gist as less true in T1",
       x = "R2: % extracting the misleading implicature",
       y = "T1 (cold) palter GIST rating  (lower = caught it)") +
  base
save2(p6, "fig6_extraction_predicts_judgment", 7.5, 5.5)

cat("wrote fig5 + fig6 (png+pdf) to", OUT, "\n")
