# ============================================================================
# make_figures_recognition_s1_18.R
# Recognition-check figures (s1-18, 3 frontier models) + the recognition->
# judgment decomposition ("blind vs knowing tolerance").
#   fig7 - recognition profile: R1/R2/R3 per model, OFFLINE vs ONLINE
#   fig8 - item-level scatter: R2 extraction -> T1 cold GIST and UNETHICAL
#   fig9 - blind vs knowing tolerance: palter U by recognition group,
#          cold vs informed, with WT/BF benchmark lines
# PNG + PDF to results/figures_combined_26/. Markers left off.
# ============================================================================

suppressPackageStartupMessages({ library(ggplot2); library(dplyr); library(tidyr) })

OUT <- "results/figures_combined_26"
model_labs <- c(gemini35flash = "Gemini 3.5 Flash", gpt56sol = "GPT-5.6-sol", opus48 = "Opus 4.8")
base <- theme_minimal(base_size = 12) +
  theme(panel.grid.minor = element_blank(), plot.title = element_text(face = "bold"))
save2 <- function(p, name, w, h) {
  ggsave(file.path(OUT, paste0(name, ".png")), p, width = w, height = h, dpi = 150)
  ggsave(file.path(OUT, paste0(name, ".pdf")), p, width = w, height = h)
}

## ---- fig7: recognition profile, offline vs online --------------------------
prof <- read.csv(file.path(OUT, "recognition_profile_s1_18.csv"), check.names = FALSE) %>%
  pivot_longer(-c(model, arm), names_to = "probe", values_to = "pct") %>%
  mutate(mlab = model_labs[model],
         probe = factor(probe, levels = c("R1: sees palter verbatim-true",
                                          "R2: extracts misleading gist",
                                          "R3: knows false gist is false")),
         arm = factor(arm, levels = c("offline", "online")))
p7 <- ggplot(prof, aes(mlab, pct, fill = arm)) +
  geom_col(position = position_dodge(0.75), width = 0.68) +
  geom_text(aes(label = sprintf("%.0f", pct)), position = position_dodge(0.75),
            vjust = -0.35, size = 3) +
  facet_wrap(~probe) +
  scale_fill_manual(values = c(offline = "grey65", online = "#1f77b4")) +
  scale_y_continuous(limits = c(0, 108), breaks = seq(0, 100, 25)) +
  labs(title = "Recognition check on the palter (s1-18): offline vs online",
       subtitle = "R1 verbatim verification | R2 implicature extraction | R3 gist evaluation",
       x = NULL, y = "% correct / extracted", fill = NULL) +
  base + theme(legend.position = "top", axis.text.x = element_text(angle = 18, hjust = 1))
save2(p7, "fig7_recognition_profile_s1_18", 11, 4.8)

## ---- fig8: item-level correct extraction -> ethics judgment ------------------
# For a palter, "correctly extracting the implied gist" = recognizing that a
# reader takes away the (false) implication. Positive framing of the same rate.
it <- read.csv(file.path(OUT, "recognition_judgment_items.csv")) %>%
  filter(cell_type == "palter") %>%
  mutate(mlab = model_labs[model]) %>%
  filter(!is.na(r2_extract_on) & !is.na(uneth_cold))
ct <- cor.test(it$r2_extract_on, it$uneth_cold)
p8 <- ggplot(it, aes(r2_extract_on * 100, uneth_cold, color = mlab)) +
  geom_hline(yintercept = 4, linetype = "dotted", color = "grey60") +
  geom_smooth(aes(group = 1), method = "lm", se = TRUE, color = "grey55",
              fill = "grey88", linewidth = 0.7) +
  geom_jitter(width = 2.2, height = 0.05, size = 2.8, alpha = 0.85) +
  annotate("text", x = 8, y = 6.6,
           label = sprintf("r = %+.2f, p = %.3f (n = %d items)",
                           ct$estimate, ct$p.value, nrow(it)),
           hjust = 0, size = 3.8, color = "grey30") +
  scale_color_brewer(palette = "Set2") +
  scale_y_continuous(limits = c(1, 7), breaks = 1:7) +
  scale_x_continuous(limits = c(-4, 104), breaks = seq(0, 100, 25)) +
  labs(title = "The better a model recognizes what the palter implies, the harsher it judges it",
       subtitle = "each point = one scenario x model (s1-18); recognition from R2 (online), judgment from T1 (cold)",
       x = "R2: % of samples correctly identifying the palter's implied gist",
       y = "T1 UNETHICAL rating (1-7)", color = NULL) +
  base + theme(legend.position = "top", panel.grid = element_blank(),
               axis.line = element_line(color = "grey70"))
save2(p8, "fig8_extraction_vs_judgment_items", 9, 5.8)

## ---- fig9: blind vs knowing tolerance ---------------------------------------
gr <- read.csv(file.path(OUT, "tolerance_groups.csv")) %>%
  mutate(group = factor(group, levels = unique(group)),
         arm = factor(ifelse(arm == "cold", "cold", "informed"), levels = c("cold", "informed")))
p9 <- ggplot(gr, aes(group, U, fill = arm)) +
  geom_col(position = position_dodge(0.72), width = 0.65) +
  geom_errorbar(aes(ymin = U - 1.96 * se, ymax = U + 1.96 * se),
                position = position_dodge(0.72), width = 0.2, linewidth = 0.5) +
  geom_text(aes(label = sprintf("%.2f", U)), position = position_dodge(0.72),
            vjust = -1.6, size = 3.3) +
  geom_hline(yintercept = 4.64, linetype = "dashed", color = "#d62728") +
  annotate("text", x = 0.62, y = 4.85, label = "blatant falsehood (4.64)",
           size = 3.2, color = "#d62728", hjust = 0) +
  geom_hline(yintercept = 1.11, linetype = "dashed", color = "#2ca02c") +
  annotate("text", x = 0.62, y = 1.32, label = "whole truth (1.11)",
           size = 3.2, color = "#2ca02c", hjust = 0) +
  scale_fill_manual(values = c(cold = "grey65", informed = "#ff7f0e")) +
  scale_y_continuous(limits = c(0, 6), breaks = 1:6) +
  labs(title = "Blind vs knowing tolerance of palters (s1-18, 3 frontier models)",
       subtitle = "palter items grouped by the model's own recognition (R2 extraction + R3 knowledge); n = 11 / 5 / 35",
       x = "recognition of the palter's misleading gist",
       y = "mean UNETHICAL (1-7)", fill = NULL) +
  base + theme(legend.position = "top")
save2(p9, "fig9_blind_vs_knowing_tolerance", 9, 5.6)

## ---- fig10: recognition -> judgment, PALTER vs TRUTHY FALSEHOOD --------------
# "Correctly identifying the implied gist" is cell-appropriate: for a palter the
# implied gist is the FALSE one; for a truthy falsehood it is the TRUE one.
it2 <- read.csv(file.path(OUT, "recognition_judgment_items.csv")) %>%
  filter(cell_type %in% c("palter", "truthy_falsehood")) %>%
  mutate(mlab = model_labs[model],
         cell = ifelse(cell_type == "palter",
                       "Palter (V+ G-): implied gist is FALSE",
                       "Truthy falsehood (V- G+): implied gist is TRUE")) %>%
  filter(!is.na(r2_extract_on) & !is.na(uneth_cold))
ann <- it2 %>% group_by(cell) %>%
  summarise(lab = { ct <- cor.test(r2_extract_on, uneth_cold)
                    sprintf("r = %+.2f, p = %.3f (n = %d)", ct$estimate, ct$p.value, n()) },
            .groups = "drop")
p10 <- ggplot(it2, aes(r2_extract_on * 100, uneth_cold, color = mlab)) +
  geom_hline(yintercept = 4, linetype = "dotted", color = "grey60") +
  geom_smooth(aes(group = 1), method = "lm", se = TRUE, color = "grey55",
              fill = "grey88", linewidth = 0.7) +
  geom_jitter(width = 2.2, height = 0.05, size = 2.6, alpha = 0.85) +
  geom_text(data = ann, aes(x = 4, y = 6.7, label = lab),
            inherit.aes = FALSE, hjust = 0, size = 3.7, color = "grey30") +
  facet_wrap(~cell) +
  scale_color_brewer(palette = "Set2") +
  scale_y_continuous(limits = c(1, 7), breaks = 1:7) +
  scale_x_continuous(limits = c(-4, 104), breaks = seq(0, 100, 25)) +
  labs(title = "Recognition raises condemnation only when the implied gist is FALSE",
       subtitle = "each point = one scenario x model (s1-18); recognition from R2 (online), judgment from T1 (cold)",
       x = "R2: % of samples correctly identifying the statement's implied gist",
       y = "T1 UNETHICAL rating (1-7)", color = NULL) +
  base + theme(legend.position = "top", panel.grid = element_blank(),
               axis.line = element_line(color = "grey70"))
save2(p10, "fig10_extraction_vs_judgment_pa_tf", 11.5, 5.8)

cat("wrote fig7, fig8, fig9, fig10 to", OUT, "\n")
