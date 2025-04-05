from pymoo.visualization.scatter import Scatter

# 최적화 과정(진화 과정)을 시각적으로 기록하는 함수 -> 세대별 진화 과정이 담긴 .mp4 영상 파일임(알고리즘이 어떻게 해를 점점 더 최적화해 나가는지를 애니메이션으로 보여줌)
def record(res, filename="Res.mp4"):
    # use the video writer as a resource
    with Recorder(Video(filename)) as rec:

        # for each algorithm object in the history
        for entry in res.history:
            sc = Scatter(title=("Gen %s" % entry.n_gen))
            sc.add(entry.pop.get("F"))
            sc.add(entry.problem.pareto_front(), plot_type="line", color="black", alpha=0.7)
            sc.do()

            # finally record the current visualization to the video
            rec.record()
