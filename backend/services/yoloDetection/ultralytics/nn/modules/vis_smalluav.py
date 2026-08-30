# ultralytics/nn/modules/vis_smalluav.py
"""
Custom modules for visible-light small UAV detection.

- VMRDBlock (Visible Multi-Receptive Detail Block):
    Multi-receptive-field feature enhancement + channel & spatial attention,
    designed for small-object detection in complex visible-light scenes.

- EdgeGradientAttention:
    Edge-Gradient Attention Block (EGAB), uses fixed multi-directional
    gradient filters + local contrast to build a spatial attention map,
    applied on low-level feature maps to enhance small high-frequency objects
    (e.g., small UAVs) and suppress smooth background.
"""

from __future__ import annotations

from typing import List, Tuple, Optional, Union

import torch
import torch.nn as nn
import torch.nn.functional as F


# -------------------------------------------------------------------------
# 1. VMRDBlock: Visible Multi-Receptive Detail Block
# -------------------------------------------------------------------------


class VMRDBlock(nn.Module):
    """
    VMRDBlock: Visible Multi-Receptive Detail Block.

    Args:
        c1 (int): Number of input channels.
        c2 (int): Number of output channels.
        reduction (int, optional): Reduction ratio for channel attention.
            Default: 8.

    Input:
        x: Tensor of shape [B, c1, H, W]

    Output:
        out: Tensor of shape [B, c2, H, W]

    Design:
        1) Low-level conv: 3x3 conv + BN + SiLU to normalize / project input.
        2) Three parallel depthwise conv branches with different receptive fields:
           - branch3: 3x3 depthwise conv (fine details)
           - branch5: 3x3 depthwise conv with dilation=2 (approx 5x5)
           - branch7: 3x3 depthwise conv with dilation=3 (approx 7x7)
        3) Concatenate branch outputs, merge via 1x1 conv back to c2 channels.
        4) Channel attention (SE-like) + spatial attention (avg+max pooling).
        5) Residual connection from input (projected to c2 channels).
    """

    def __init__(self, c1: int, c2: int, reduction: int = 8) -> None:
        super().__init__()
        self.c1 = c1
        self.c2 = c2

        mid_channels = c1  # keep mid channels same as input for simplicity

        # 1) Low-level conv
        self.low_conv = nn.Sequential(
            nn.Conv2d(c1, mid_channels, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.SiLU(inplace=True),
        )

        # 2) Multi-receptive-field branches (depthwise conv to save params)
        self.branch3 = nn.Sequential(
            nn.Conv2d(mid_channels, mid_channels, kernel_size=3, padding=1, groups=mid_channels, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.SiLU(inplace=True),
        )
        self.branch5 = nn.Sequential(
            nn.Conv2d(mid_channels, mid_channels, kernel_size=3, padding=2, dilation=2, groups=mid_channels, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.SiLU(inplace=True),
        )
        self.branch7 = nn.Sequential(
            nn.Conv2d(mid_channels, mid_channels, kernel_size=3, padding=3, dilation=3, groups=mid_channels, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.SiLU(inplace=True),
        )

        # 3) Merge branches back to c2 channels
        self.merge_conv = nn.Conv2d(mid_channels * 3, c2, kernel_size=1, bias=False)
        self.merge_bn = nn.BatchNorm2d(c2)

        # 4) Channel Attention (SE-like)
        #   Global average pooling -> FC -> ReLU -> FC -> Sigmoid
        hidden_ch = max(c2 // reduction, 8)
        self.ca = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(c2, hidden_ch, kernel_size=1, bias=False),
            nn.SiLU(inplace=True),
            nn.Conv2d(hidden_ch, c2, kernel_size=1, bias=False),
            nn.SigLU() if hasattr(nn, "SigLU") else nn.Sigmoid(),  # fallback for older torch
        )

        # 5) Spatial Attention (CBAM-style)
        self.sa_conv = nn.Conv2d(2, 1, kernel_size=7, padding=3, bias=False)

        # 6) Residual projection to match channel dims
        if c1 != c2:
            self.proj = nn.Conv2d(c1, c2, kernel_size=1, bias=False)
        else:
            self.proj = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, c1, H, W]
        b, _, h, w = x.shape

        # (1) low-level conv
        low = self.low_conv(x)  # [B, mid, H, W]

        # (2) multi-receptive branches
        feat3 = self.branch3(low)
        feat5 = self.branch5(low)
        feat7 = self.branch7(low)

        merged = torch.cat([feat3, feat5, feat7], dim=1)  # [B, 3*mid, H, W]
        merged = self.merge_bn(self.merge_conv(merged))   # [B, c2, H, W]

        # (3) channel attention
        ca_weight = self.ca(merged)  # [B, c2, 1, 1]
        merged_ca = merged * ca_weight

        # (4) spatial attention
        avg_pool = torch.mean(merged_ca, dim=1, keepdim=True)             # [B,1,H,W]
        max_pool, _ = torch.max(merged_ca, dim=1, keepdim=True)          # [B,1,H,W]
        sa_input = torch.cat([avg_pool, max_pool], dim=1)                # [B,2,H,W]
        sa_weight = torch.sigmoid(self.sa_conv(sa_input))                # [B,1,H,W]
        merged_casa = merged_ca * sa_weight                              # [B,c2,H,W]

        # (5) residual connection
        res = self.proj(x)  # [B,c2,H,W]
        out = merged_casa + res
        return out


# -------------------------------------------------------------------------
# 2. EdgeGradientAttention: Edge-Gradient Attention Block
# -------------------------------------------------------------------------


# ultralytics/nn/modules/vis_smalluav.py 中替换 EdgeGradientAttention 类

class EdgeGradientAttention(nn.Module):
    """
    EGAB: Edge-Gradient Attention Block

    用于可见光小无人机场景的边缘/对比度空间注意力模块。

    Args:
        c_feat (int): 要被调制的特征图通道数（例如 P3 的通道数）。
        attn_ratio (float, optional): 注意力的缩放强度，默认为 0.5。

    使用方式（在 Ultralytics 中）:
        - YAML 中写:  from: [idx_shallow, idx_feat], module: EdgeGradientAttention, args: [attn_ratio]
        - parse_model 会调用: EdgeGradientAttention(c_feat, attn_ratio)
        - forward 时会收到 x = [shallow_feat, feat]:
            shallow_feat: [B, C_ref, H_ref, W_ref]   (浅层特征或原图特征)
            feat        : [B, C_feat, H_feat, W_feat] (需要被增强的特征, 通道数 = c_feat)

    处理流程:
        1) 将 shallow_feat 在通道维做平均得到 1 通道灰度图 gray。
        2) 若 gray 与 feat 的空间尺寸不一致，插值 gray 到 feat 的尺寸。
        3) 对 gray 应用四个固定的梯度卷积核 (Sobel x/y + 对角线) 得到 4 通道梯度图。
        4) 通过 3x3 AvgPool 计算局部均值, 得到局部对比度 contrast = |gray - mean_local|.
        5) 将 [grad_maps, contrast] 拼接，通过 2 层小卷积获得空间注意力图 attn ∈ [0,1]。
        6) 对 feat 做残差式调制: feat_out = feat * (1 + attn_ratio * attn)。
    """

    def __init__(self, c_feat: int, attn_ratio: float = 0.5) -> None:
        super().__init__()
        self.c_feat = int(c_feat)
        self.attn_ratio = float(attn_ratio)

        # 四个 Sobel-like 梯度核: 水平、垂直、45°、135°
        kx = torch.tensor([[[-1.0, 0.0, 1.0],
                            [-2.0, 0.0, 2.0],
                            [-1.0, 0.0, 1.0]]])
        ky = torch.tensor([[[-1.0, -2.0, -1.0],
                            [ 0.0,  0.0,  0.0],
                            [ 1.0,  2.0,  1.0]]])
        k45 = torch.tensor([[[0.0,  1.0,  2.0],
                             [-1.0, 0.0,  1.0],
                             [-2.0,-1.0, 0.0]]])
        k135 = torch.tensor([[[ 2.0, 1.0, 0.0],
                              [ 1.0, 0.0,-1.0],
                              [ 0.0,-1.0,-2.0]]])
        kernels = torch.stack([kx, ky, k45, k135], dim=0)  # [4,1,3,3]

        # 固定权重的 gradient 卷积
        self.grad_conv = nn.Conv2d(
            in_channels=1,
            out_channels=4,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False,
        )
        with torch.no_grad():
            self.grad_conv.weight.copy_(kernels)
        for p in self.grad_conv.parameters():
            p.requires_grad = False

        # 局部对比度: 3x3 均值池化
        self.local_pool = nn.AvgPool2d(kernel_size=3, stride=1, padding=1)

        # 小卷积网络: [4梯度 + 1对比度] -> 1通道注意力图
        self.attn_conv = nn.Sequential(
            nn.Conv2d(5, 16, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.SiLU(inplace=True),
            nn.Conv2d(16, 1, kernel_size=1, stride=1, padding=0, bias=True),
            nn.Sigmoid(),  # 输出 attn ∈ [0,1]
        )
        
        # Init last conv bias to negative so attn starts near 0
        nn.init.constant_(self.attn_conv[-2].bias, -5.0)

    def forward(
        self,
        x: Union[torch.Tensor, List[torch.Tensor], Tuple[torch.Tensor, torch.Tensor]],
    ) -> torch.Tensor:
        """
        Args:
            x: list/tuple [shallow_feat, feat]
                shallow_feat: [B,C_ref,H_ref,W_ref] (较浅层特征)
                feat        : [B,c_feat,H_feat,W_feat] (待增强特征)

        Returns:
            feat_out: [B,c_feat,H_feat,W_feat]
        """
        if isinstance(x, (list, tuple)):
            shallow, feat = x
        else:
            raise TypeError(
                "EdgeGradientAttention expects a list/tuple of [shallow_feat, feat]. "
                f"Got type: {type(x)}"
            )

        assert shallow.dim() == 4 and feat.dim() == 4, "inputs must be 4D tensors"
        B1, C_ref, H_ref, W_ref = shallow.shape
        B2, C_feat, H_feat, W_feat = feat.shape
        assert B1 == B2, "Batch size mismatch between shallow_feat and feat"
        assert C_feat == self.c_feat, (
            f"Feature channel mismatch: expected {self.c_feat}, got {C_feat}"
        )

        # 1) 将 shallow_feat 转为灰度: 对通道求平均
        gray = shallow.mean(dim=1, keepdim=True)  # [B,1,H_ref,W_ref]

        # 2) 若尺寸与 feat 不一致，则插值到 feat 的尺寸
        if H_ref != H_feat or W_ref != W_feat:
            gray = F.interpolate(gray, size=(H_feat, W_feat),
                                 mode="bilinear", align_corners=False)  # [B,1,H_feat,W_feat]

        # 3) 多方向梯度图 (固定卷积)
        grad_maps = self.grad_conv(gray)  # [B,4,H_feat,W_feat]

        # 4) 局部对比度 (灰度 - 周围均值)
        local_mean = self.local_pool(gray)         # [B,1,H_feat,W_feat]
        contrast = (gray - local_mean).abs()       # [B,1,H_feat,W_feat]

        # 5) 拼接梯度+对比度，生成空间注意力图
        attn_in = torch.cat([grad_maps, contrast], dim=1)  # [B,5,H_feat,W_feat]
        attn_map = self.attn_conv(attn_in)                 # [B,1,H_feat,W_feat], [0,1]

        # 6) 残差式调制特征
        feat_out = feat * (1.0 + self.attn_ratio * attn_map)
        return feat_out
