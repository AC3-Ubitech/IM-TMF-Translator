#! /bin/bash
parent_dir="$(dirname "$(pwd)")"

alias k4="kubectl --kubeconfig $parent_dir/kubeconfigs/cluster-4.yaml"
alias kh="kubectl --kubeconfig $parent_dir/kubeconfigs/AC3-kubeconfig.ymal"