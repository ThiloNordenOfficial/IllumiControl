
import tensorflow as tf

tf.compat.v1.disable_eager_execution()

import os
import sys


def load_graph_def_from_checkpoint(checkpoint_dir: str) -> tf.compat.v1.GraphDef:
    """
    Loads the GraphDef from the .meta file associated with the latest checkpoint.
    """
    ckpt_state = tf.train.get_checkpoint_state(checkpoint_dir)
    if not ckpt_state or not ckpt_state.model_checkpoint_path:
        raise FileNotFoundError(f"No checkpoint found in {checkpoint_dir}")

    ckpt_path = ckpt_state.model_checkpoint_path
    meta_path = ckpt_path + ".meta"
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Meta graph file not found: {meta_path}")

    # Reset any existing graph and import the meta graph (no session needed)
    tf.compat.v1.reset_default_graph()
    # The import creates a default graph; we can now fetch its GraphDef
    graph_def = tf.compat.v1.get_default_graph().as_graph_def()
    return graph_def


def get_placeholder_tensor_names(graph_def: tf.compat.v1.GraphDef) -> list[str]:
    """
    Returns a list of placeholder tensor names (e.g. ['input_1:0']).
    """
    placeholders = []
    for node in graph_def.node:
        if node.op == "Placeholder":
            # Tensor name is node.name + ':0' (first output)
            placeholders.append(f"{node.name}:0")
    return placeholders


def main():
    if len(sys.argv) != 2:
        print("Usage: python model-extractor.py /path/to/checkpoint_dir")
        sys.exit(1)

    checkpoint_dir = sys.argv[1]
    if not os.path.isdir(checkpoint_dir):
        raise NotADirectoryError(f"'{checkpoint_dir}' is not a valid directory")

    graph_def = load_graph_def_from_checkpoint(checkpoint_dir)
    placeholders = get_placeholder_tensor_names(graph_def)
    if placeholders:
        print("\n🔎 Detected placeholder tensors (possible inputs):")
        for ph in placeholders:
            print(f"   • {ph}")
    else:
        print("\n⚠️  No Placeholder nodes found in the GraphDef.")


if __name__ == "__main__":
    main()