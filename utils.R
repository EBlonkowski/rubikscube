
# Apply a permutation to the index of a vector
apprec <- function(gp) {
  function(...) {
    f <- c(...)
    f[as.word(gp) %>% unclass %>% c]
  }
}