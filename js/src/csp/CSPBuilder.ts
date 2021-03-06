import * as widgets from "@jupyter-widgets/base";
import { timeout } from "d3";
import Vue from "vue";
import { IEvent } from "../Events";
import { Graph, ICSPGraphNode } from "../Graph";
import { d3ForcePlusRelativeLayout, GraphLayout, relativeLayout } from "../GraphLayout";
import CSPGraphBuilder from "./components/CSPBuilder.vue";
import CSPBuilderModel from "./CSPBuilderModel";
declare let Jupyter: any;

/**
 * Creates a view to construct a CSP. Interfaces with Jupyter backend.
 *
 * See the accompanying backend file: `aispace2/jupyter/csp/cspbuilder.py`.
 */
export default class CSPBuilder extends widgets.DOMWidgetView {
  public model: CSPBuilderModel;
  public vue: Vue;

  public initialize(opts: any) {
    super.initialize(opts);
  }

  public render() {
    const initialGraph = this.model.graph;

    timeout(() => {
      this.vue = new CSPGraphBuilder({
        data: {
          graph: initialGraph,
          textSize: this.model.textSize,
          lineWidth: this.model.lineWidth,
          layout: new GraphLayout(d3ForcePlusRelativeLayout(), relativeLayout()),
          detailLevel: this.model.detailLevel,
          decimalPlace: this.model.decimalPlace
        },
        watch: {
          graph: {
            handler: (val: Graph, oldVal: Graph) => {
              // Creating a copy is necessary as changes are detected by reference by traitlets
              this.model.graph = Graph.fromJSON(oldVal.toJSON()) as Graph<
                ICSPGraphNode
              >;
              this.touch();
            },
            deep: true
          }
        }
      }).$mount(this.el);
    });

    return this;
  }

  public remove() {
    if (this.vue != null) {
      this.vue.$destroy();
    }
  }
}
