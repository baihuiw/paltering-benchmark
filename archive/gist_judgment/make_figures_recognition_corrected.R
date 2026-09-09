# ============================================================================
# make_figures_recognition_corrected.R
# Redraws fig5/fig6 after recoding the palter R2 "other" free-text gists:
#   MISLEADING  -> Extracted (the model DID get the palter's implicature)
#   ACCURATE    -> Wrong      (read the palter as debunking; didn't extract)
#   HEDGED      -> grey       (explicitly withheld judgment)
# fig5 - stacked composition per model (corrected R2)
# fig6 - corrected extraction% vs T1-cold palter GIST
# Overwrites the earlier (artifact-inflated) fig5/fig6. PNG + PDF.
# ============================================================================

suppressPackageStartupMessages({ library(ggplot2); library(dplyr); library(tidyr) })

OUT <- "results/figures_pilot_s19_26"
d   <- read.csv(file.path(OUT, "r2_corrected.csv"), stringsAsFactors = FALSE)
model_labs <- c(gemini35flash = "Gemini 3.5 Flash", gpt56sol = "GPT-5.6-sol",
                opus48 = "Opus 4.8", qwen37plus = "Qwen 3.7+", deepseekv4pro = "DeepSeek v4-pro")
d$mlab <- model_labs[d$model]
base <- theme_minimal(base_size = 12) +
  theme(panel.grid.minor = element_blank(), plot.title = element_text(face = "bold"))
save2 <- function(p, name, w, h) {
  ggsave(file.path(OUT, paste0(name, ".png")), p, width = w, height = h, dpi = 150)
  ggsave(file.path(OUT, paste0(name, ".pdf")), p, width = w, height = h)
}

cat_levels <- c("Extracted the implicature", "Wrong (read as debunking)", "Hedged (no commitment)")
cat_cols <- c("Extracted the implicature" = "#ff7f0e",
              "Wrong (read as debunking)" = "#d62728",
              "Hedged (no commitment)"    = "grey70")

## FIG 5 (redraw) - stacked corrected composition per model
long <- d %>%
  transmute(mlab,
            `Extracted the implicature` = extracted,
            `Wrong (read as debunking)` = wrong,
            `Hedged (no commitment)`    = hedged) %>%
  pivot_longer(-mlab, names_to = "cat", values_to = "pct") %>%
  mutate(cat = factor(cat, levels = rev(cat_levels)),
         mlab = factor(mlab, levels = d$mlab[order(d$extracted)]))
p5 <- ggplot(long, aes(mlab, pct, fill = cat)) +
  geom_col(width = 0.72) +
  geom_text(data = subset(long, pct >= 5), aes(label = sprintf("%.0f%%", pct)),
            position = position_stack(vjust = 0.5), size = 3.2, color = "white") +
  scale_fill_manual(values = cat_cols, breaks = cat_levels) +
  scale_y_continuous(limits = c(0, 100), breaks = seq(0, 100, 25), expand = c(0, 0)) +
  coord_flip() +
  labs(title = "Corrected palter extraction (R2, 'other' free-text re-coded)",
       subtitle = "reading the free text, models mostly DID get the misleading gist; evaluation (R3) is ~100% throughout",
       x = NULL, y = "% of palter samples", fill = NULL) +
  base + theme(legend.position = "top")
save2(p5, "fig5_palter_decomposition", 9, 5)

## FIG 6 (redraw) - corrected extraction vs T1-cold palter GIST
p6 <- ggplot(d, aes(extracted, t1_cold_gist)) +
  geom_hline(yintercept = 4, linetype = "dotted", color = "grey60") +
  geom_smooth(method = "lm", se = FALSE, color = "grey75", linewidth = 0.7) +
  geom_point(size = 3, color = "#ff7f0e") +
  geom_text(aes(label = mlab), vjust = -0.9, size = 3.4) +
  scale_x_continuous(limits = c(60, 100)) +
  scale_y_continuous(limits = c(2.5, 5), breaks = seq(2.5, 5, 0.5)) +
  labs(title = "Corrected extraction vs palter judgment",
       subtitle = "with the coding artifact removed, extraction is high (65-92%) and no longer tracks the T1 gist gap",
       x = "Corrected R2: % extracting the misleading implicature",
       y = "T1 (cold) palter GIST rating  (lower = caught it)") +
  base
save2(p6, "fig6_extraction_predicts_judgment", 7.5, 5.5)

cat("redrew fig5 + fig6 (corrected) to", OUT, "\n")
