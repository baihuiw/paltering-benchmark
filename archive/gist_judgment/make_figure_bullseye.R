# ============================================================================
# make_figure_bullseye.R  (v3 — organic score bands)
# Condemnation map of all 26 topics. Distance from center = mean UNETHICAL
# over the three misinformation cells (palter/TF/blatant; cold, 3 models).
# Filled bands ARE score levels (0.5-wide, labeled wiggly white lines at
# U = 2/3/4). The radial scale breathes by angle, DATA-DRIVEN: the blob
# bulges outward in sectors whose topics are condemned more and pinches in
# lenient sectors (plus a soft irregular rim fade) — organic like a KDE,
# but every band boundary remains a true score level along its ray.
# Output: fig11_condemnation_bullseye .png/.pdf
# ============================================================================

suppressPackageStartupMessages({ library(ggplot2); library(dplyr); library(ggrepel); library(viridisLite) })

OUT <- "results/figures_combined_26"
d <- read.csv(file.path(OUT, "topic_condemnation.csv"), stringsAsFactors = FALSE)

## ---- radius = score, angle = family sector ---------------------------------
U_hi <- 4.9; U_lo <- 1.6
r_of <- function(U) 0.08 + (U_hi - U) / (U_hi - U_lo) * 0.92
fams <- c("Domestic politics & society", "Economy & markets",
          "Geopolitics & war disinfo", "Hostile smears")
gap <- 14
sizes <- sapply(fams, function(f) sum(d$family == f))
span <- (360 - gap * length(fams)) * sizes / sum(sizes)
starts <- 90 + cumsum(c(0, head(span + gap, -1)))
d$theta <- NA
for (i in seq_along(fams)) {
  idx <- which(d$family == fams[i]); idx <- idx[order(-d$U[idx])]
  k <- length(idx)
  d$theta[idx] <- starts[i] + (seq_len(k) - 0.5) / k * span[i]
}

## ---- data-driven angular "breathing" of the radial scale --------------------
# smooth angular condemnation profile (von-Mises-style kernel over topic angles)
th_pt <- -d$theta * pi / 180
Ubar <- function(a) {
  w <- exp(cos(a - th_pt) * 6)                # bw ~ 33 degrees
  sum(w * d$U) / sum(w)
}
th_grid <- seq(0, 2 * pi, length.out = 721)
prof <- sapply(th_grid, Ubar)
dev <- (prof - mean(prof)) / diff(range(prof))            # -0.5 .. +0.5
warp_tab <- 1 + 0.16 * dev + 0.030 * sin(3 * th_grid + 1.1) + 0.022 * sin(5 * th_grid + 4.0)
w_of <- function(a) warp_tab[pmin(721, pmax(1, round(((a %% (2*pi)) / (2*pi)) * 720) + 1))]

d <- d %>% mutate(a = -theta * pi / 180,
                  r = r_of(U) * w_of(a),
                  x = r * cos(a), y = r * sin(a),
                  xl = 1.24 * cos(a), yl = 1.24 * sin(a))

fam_cols <- c("Domestic politics & society" = "#31597e",
              "Economy & markets"           = "#3e7d5a",
              "Geopolitics & war disinfo"   = "#7d503e",
              "Hostile smears"              = "#6d3e7d")

## ---- painter-style discs: each score level = one organic disc ---------------
levels_lo <- seq(1.75, 4.75, by = 0.5)                      # disc = region U >= lv
band_cols <- mako(length(levels_lo), begin = 0.12, end = 0.97)
aa <- seq(0, 2 * pi, length.out = 720)
disc <- function(lv, id, scale = 1)
  data.frame(x = r_of(lv) * w_of(aa) * scale * cos(aa),
             y = r_of(lv) * w_of(aa) * scale * sin(aa), g = id)
# soft rim fade: translucent halos outside the outermost band
halos <- do.call(rbind, lapply(1:6, function(i) disc(1.75, paste0("h", i), 1 + i * 0.022)))
halo_alpha <- rep(seq(0.30, 0.05, length.out = 6), each = 720)
discs <- do.call(rbind, lapply(seq_along(levels_lo),
                               function(i) disc(levels_lo[i], sprintf("d%02d", i))))
discs$fill <- rep(band_cols, each = 720)

## ---- wiggly white contour lines at U = 2, 3, 4 + labels ---------------------
rings <- do.call(rbind, lapply(c(2, 3, 4), function(lv)
  transform(disc(lv, paste0("r", lv)), lv = lv)))
lab_a <- 135 * pi / 180
ring_lab <- data.frame(lv = c(2, 3, 4)) %>%
  mutate(x = (r_of(lv) * w_of(lab_a) + 0.045) * cos(lab_a),
         y = (r_of(lv) * w_of(lab_a) + 0.045) * sin(lab_a),
         lab = paste0("U=", lv),
         colr = c("white", "white", "white"))

famlab <- data.frame(family = fams,
                     mid = starts + span * c(0.5, 0.5, 0.97, 0.5)) %>%
  mutate(x = 1.72 * cos(-mid * pi / 180), y = 1.72 * sin(-mid * pi / 180))

p <- ggplot() +
  geom_polygon(data = halos, aes(x, y, group = g),
               fill = band_cols[1], alpha = halo_alpha) +
  geom_polygon(data = discs, aes(x, y, group = g), fill = discs$fill) +
  geom_path(data = rings, aes(x, y, group = g), color = "white",
            linewidth = 0.5, alpha = 0.95) +
  geom_text(data = ring_lab, aes(x, y, label = lab), color = ring_lab$colr,
            size = 3.0, fontface = "italic") +
  geom_segment(data = d, aes(x = x, y = y, xend = xl, yend = yl),
               color = "grey55", linewidth = 0.24, alpha = 0.65) +
  geom_point(data = d, aes(x, y), shape = 21, fill = "white",
             color = "grey10", size = 2.3, stroke = 0.55) +
  geom_text_repel(data = filter(d, x >= 0),
                  aes(xl, yl, label = sprintf("%s  %.1f", label, U), color = family),
                  size = 3.0, fontface = "bold", hjust = 0, nudge_x = 0.05,
                  direction = "y", box.padding = 0.12, min.segment.length = 10,
                  max.overlaps = Inf, show.legend = FALSE) +
  geom_text_repel(data = filter(d, x < 0),
                  aes(xl, yl, label = sprintf("%.1f  %s", U, label), color = family),
                  size = 3.0, fontface = "bold", hjust = 1, nudge_x = -0.05,
                  direction = "y", box.padding = 0.12, min.segment.length = 10,
                  max.overlaps = Inf, show.legend = FALSE) +
  geom_text(data = famlab, aes(x, y, label = family, color = family),
            size = 3.2, fontface = "bold.italic", show.legend = FALSE) +
  scale_color_manual(values = fam_cols) +
  coord_fixed(xlim = c(-2.1, 2.1), ylim = c(-1.85, 1.85), expand = FALSE) +
  labs(title = "Which topics' misinformation gets condemned most?",
       subtitle = "distance from center = mean UNETHICAL over the palter/truthy-falsehood/blatant cells (cold arm, 3 frontier models);\nfilled bands = 0.5-wide score levels, white lines mark U = 2, 3, 4; the blob bulges toward sectors condemned more",
       caption = "26 scenarios; labels show topic and mean U; radial scale breathes by angle (data-driven bulge + soft rim), bands remain true score levels along each ray") +
  theme_void(base_size = 12) +
  theme(plot.background = element_rect(fill = "white", color = NA),
        panel.background = element_rect(fill = "white", color = NA),
        plot.title = element_text(face = "bold", size = 15),
        plot.subtitle = element_text(color = "grey25", size = 9.5),
        plot.caption = element_text(color = "grey45", size = 7.6),
        plot.margin = margin(8, 10, 6, 10))

ggsave(file.path(OUT, "fig11_condemnation_bullseye.png"), p, width = 10.8, height = 9.8, dpi = 150)
ggsave(file.path(OUT, "fig11_condemnation_bullseye.pdf"), p, width = 10.8, height = 9.8)
cat("wrote fig11 (organic score bands) to", OUT, "\n")
