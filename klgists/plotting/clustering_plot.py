import pandas as pd
import seaborn as sns
from scipy.spatial.distance import squareform
from sklearn import manifold
from scipy.spatial.distance import pdist
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Union, List, Dict, Callable

def _make_pc_df(data_df: pd.DataFrame, positions: np.ndarray) -> pd.DataFrame:
    tsne_df = pd.DataFrame(positions).rename(columns={0: 'PC1', 1: 'PC2'})
    tsne_df = data_df.reset_index().merge(tsne_df, left_index=True, right_index=True).set_index(data_df.index)
    for column in data_df.columns | data_df.index.names:
        tsne_df.drop(column, axis=1, inplace=True)
    return tsne_df / tsne_df.mean()  # rescale because matplotlib's autoscale fails miserably for small values


def calc_tsne(data_df: pd.DataFrame, tsne: manifold.TSNE=manifold.TSNE(n_components=2,
              perplexity=20.0,
              early_exaggeration=4.0,
              learning_rate=300.0,
              n_iter=5000,
              n_iter_without_progress=100,
              min_grad_norm=1e-07,
              metric='euclidean',
              init='random',
              method='barnes_hut',
              angle=0.1),
        random_seed: Optional[int]=None) -> pd.DataFrame:
    """This function doesn't really do anything; it's just a reminder of how to run tSNE.
    data_df should be a dataframe containing only the data to run through tSNE (but other data in the index is ok).
    """
    tsne.random_state = None if random_seed is None else np.random.RandomState(seed=random_seed)
    positions = tsne.fit_transform(data_df.values)
    return _make_pc_df(data_df, positions)


def calc_mds_and_pca(S: pd.DataFrame,
        is_metric: bool=True,
        distance: Union[str, Callable[[np.ndarray], np.ndarray]]='euclidean',
        random_seed: Optional[int]=None,
        max_iter: int=3000,
        convergence_tolerance: float=1e-9) -> pd.DataFrame:
    positions = calc_mds_only(S, 2, is_metric=is_metric, distance=distance, random_seed=random_seed, max_iter=max_iter, convergence_tolerance=convergence_tolerance)
    pca = PCA(n_components=2)
    positions = pca.fit_transform(positions)
    return _make_pc_df(data_df, positions)


def calc_mds_only(data_df: pd.DataFrame, n_components: int,
        distance: Union[str, Callable[[np.ndarray], np.ndarray]]='euclidean',
        is_metric: bool=True,
        random_seed: Optional[int]=None,
        max_iter: int=3000,
        convergence_tolerance: float=1e-9) -> pd.DataFrame:
    seed = None if random_seed is None else np.random.RandomState(seed=random_seed)
    # for whatever reason, MDS only allows dissimilarity='precomputed' or dissimilarity='euclidean'
    dissimilarities = squareform(pdist(data_df.values, distance))
    # Note: n_jobs>1 hangs indefinitely
    mds = manifold.MDS(n_components=n_components, metric=is_metric, max_iter=max_iter, eps=convergence_tolerance, random_state=seed, dissimilarity='precomputed')
    positions = mds.fit_transform(dissimilarities)
    return _make_pc_df(data_df, positions)


def plot_tsne(tsne_df: pd.DataFrame,
        colors: Optional[Dict[str, str]]=None, markers: Optional[List[str]]=None, sizes: Union[float, List[float]]=100, hue_column: str='class',
        size: float=10, aspect: float = 1,
        show_ticks: bool=False, style: str='whitegrid', font_scale: float=1.4, legend_font_scale: float=20) -> sns.FacetGrid:
    sns.set(font_scale=font_scale)
    sns.set_style(style)
    if markers is None:  # setting markers=None results in no markers
        plot = sns.lmplot('PC2', 'PC1', tsne_df, hue=hue_column, fit_reg=False, size=10, aspect=1, palette=colors, scatter_kws={'s': sizes})
    else:
        plot = sns.lmplot('PC2', 'PC1', tsne_df, hue=hue_column, fit_reg=False, size=10, aspect=1, palette=colors, markers=markers, scatter_kws={'s': sizes})
    if not show_ticks:
        plot.ax.set_xticks([])
        plot.ax.set_yticks([])
    legend = plot.fig.legends[0]
    legend.prop.set_size(legend_font_scale)
    legend.set_title(None)
    return plot
    