/*
Copyright 2017 Rice University

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
package edu.rice.cs.caper.bayou.application.dom_driver;

import com.google.gson.annotations.Expose;
import edu.rice.cs.caper.bayou.core.dsl.DSubTree;
import edu.rice.cs.caper.bayou.core.dsl.Sequence;
import org.eclipse.jdt.core.dom.InfixExpression;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class DOMInfixExpression extends DOMExpression implements Handler {

    final InfixExpression expr;

    @Expose
    final String node = "DOMInfixExpression";

    @Expose
    DOMExpression _left;

    @Expose
    DOMExpression _right;

    @Expose
    String _operator; // terminal

    public DOMInfixExpression(InfixExpression expr) {
        this.expr = expr;
        this._left = new DOMExpression(expr.getLeftOperand()).handleAML();
        this._right = new DOMExpression(expr.getRightOperand()).handleAML();
        this._operator = expr.getOperator().toString();
    }

    @Override
    public DSubTree handle() {
        DSubTree tree = new DSubTree();

        DSubTree Tleft = new DOMExpression(expr.getLeftOperand()).handle();
        DSubTree Tright = new DOMExpression(expr.getRightOperand()).handle();

        tree.addNodes(Tleft.getNodes());
        tree.addNodes(Tright.getNodes());

        return tree;
    }

    @Override
    public DOMInfixExpression handleAML() {
        return this;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || !(o instanceof DOMInfixExpression))
            return false;
        DOMInfixExpression d = (DOMInfixExpression) o;
        return _left.equals(d._left) && _right.equals(d._right);
    }

    @Override
    public int hashCode() {
        return 7* _left.hashCode() + 17* _right.hashCode();
    }

    @Override
    public Set<String> bagOfAPICalls() {
        Set<String> calls = new HashSet<>();
        calls.addAll(_left.bagOfAPICalls());
        calls.addAll(_right.bagOfAPICalls());
        return calls;
    }

    @Override
    public void updateSequences(List<Sequence> soFar, int max, int max_length)
            throws TooManySequencesException, TooLongSequenceException {
        _left.updateSequences(soFar, max, max_length);
        _right.updateSequences(soFar, max, max_length);
    }

    @Override
    public int numStatements() {
        return 0;
    }

    @Override
    public int numLoops() {
        return 0;
    }

    @Override
    public int numBranches() {
        return 0;
    }

    @Override
    public int numExcepts() {
        return 0;
    }
}
